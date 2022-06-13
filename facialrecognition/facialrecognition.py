import base64
import datetime
import json
import logging as logger
import os
import pickle
import time
from contextlib import closing
from multiprocessing import Pool
from tempfile import gettempdir
from typing import Dict

import cv2
import psycopg2
import pytz
from botocore.exceptions import BotoCoreError, ClientError
from helper import AbstractClientHelper
from playsound import playsound

logger = logger.getLogger()


def crop_image_via_bounding_box(image: bytearray, height: int, width: int, bounding_box: str, epoch_time: int, face_number: int) -> str:
    """ Crops the image based on the bounding box coordinates, returning the filepath to the newly cropped image.

    Args:
        image (bytearray): Original image to be croppped.
        height (int): Height in pixels of the original image.
        width (int): Width in pixels of the original image.
        bounding_box (str): Boundary box coordinates of the face.
        epoch_time (int): Epoch time to save with the image.
        face_number (int): Face number to save with the image.

    Returns:
        str: Filepath to the cropped image.
    """
    w = int(bounding_box['Width'] * width)
    h = int(bounding_box['Height'] * height)
    x = int(bounding_box['Left'] * width)
    y = int(bounding_box['Top'] * height)
    cropped_image = image[y:y + h, x:x + w]
    cropped_image_name = f"open_cv_frame_{epoch_time}_cropped_{face_number}.png"
    cv2.imwrite(cropped_image_name, cropped_image)
    return cropped_image_name


def write_to_climb_db(secret: str, user_id: str, climb_date: datetime) -> None:
    """ Writes the face id and date to the climb database.

    Args:
        secret (str): AWS Secrets Manager secret.
        user_id (list): User ID which is the Face ID to be written to the climb database.
        climb_date (datetime): Current datetime in year-month-day format.
    """
    database = secret['dbInstanceIdentifier']
    user = secret['username']
    password = secret['password']
    host = secret['host_ip']
    port = secret['port']

    try:
        conn = psycopg2.connect(
            database=database,
            user=user,
            password=password,
            host=host,
            port=port)
        logger.debug("Database connection opened...")
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO climbs (user_id, climb_date) VALUES (%s, %s)",
            (user_id,
                climb_date))
        conn.commit()
        logger.debug("Record inserted successfully...")
        conn.close()
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        logger.error("Database connection failed...")
        raise(error)


def get_current_date() -> datetime:
    """ Returns the current date in year-month-day format.

    Returns:
        datetime: Current date in year-month-day format.
    """
    return datetime.date.today()


class PollyHelper(AbstractClientHelper):

    def __init__(self, aws_session=None, *args, **kwargs):
        super(PollyHelper, self).__init__('polly', aws_session)

    def synthesize_speech(self, text: str) -> None:
        """ Synthesizes speech from the given text via AWS Polly, padding the input text with SSML tags for cleaner speech.

        Args:
            text (str): Text to be synthesized.

        Raises:
            BotoCoreError: Boto core error.
            ClientError: Boto3 client error.
            Exception: "Could not stream audio!"
        """
        speech = "<speak><amazon:effect name='drc'><prosody volume='+6dB'>" + text + "</prosody></amazon:effect></speak>"
        try:
            # Request speech synthesis
            response = self.client.synthesize_speech(Engine="neural", Text=speech, TextType="ssml", OutputFormat="mp3", VoiceId="Joanna")
        except (BotoCoreError, ClientError) as error:
            # The service returned an error, exit gracefully
            self.logger.error(error)
            raise error

        # Access the audio stream from the response
        if "AudioStream" in response:
            # Note: Closing the stream is important because the service throttles on the
            # number of parallel connections. Here we are using contextlib.closing to
            # ensure the close method of the stream object will be called automatically
            # at the end of the with statement's scope.
            with closing(response["AudioStream"]) as stream:
                output = os.path.join(gettempdir(), "speech.mp3")

                try:
                    # Open a file for writing the output as a binary stream
                    with open(output, "wb") as file:
                        file.write(stream.read())
                except IOError as error:
                    # Could not write to file, exit gracefully
                    self.logger.error(error)
                    raise error

        else:
            # The response didn't contain audio data, exit gracefully
            self.logger.error("Could not stream audio!")
            raise Exception('Could not stream audio!')

        # Play the audio file
        playsound(output)


class RekognitionHelper(AbstractClientHelper):

    def __init__(self, aws_session=None, *args, **kwargs):
        super(RekognitionHelper, self).__init__('rekognition', aws_session)

    def search_faces_by_image(self, photo: str, jgCollectionId: str) -> Dict:
        """ Compares the faces in the photo with the faces in the collection via AWS Rekognition and returns a dictionary of face ids and names.

        Args:
            photo (bytearray): Photo taken via webcam.
            collectionId (str): Rekognition Face ID collection.

        Returns:
            Dict: Key is face id, value is face name.
        """
        try:
            with open(photo, 'rb') as image:
                response = self.client.search_faces_by_image(
                    CollectionId=jgCollectionId,
                    Image={
                        'Bytes': image.read()
                    },
                    FaceMatchThreshold=90,
                    MaxFaces=1)
                face_id = response['FaceMatches'][0]['Face']['FaceId']
                face_name = response['FaceMatches'][0]['Face']['ExternalImageId'].split('_')[0]
        except ClientError as error:
            if error.response['Error'] == {'Code': 'InvalidParameterException'}:
                self.logger.error("There are no faces in this image!")

        if response['FaceMatches']:
            return face_id, face_name
        else:
            self.logger.error("You are not in the collection!")
            return None, None

    def detect_faces(self, photo: str) -> bool:
        """ Detects faces in the photo via AWS Rekognition and returns a boolean if any usable faces are present.

        Args:
            photo (bytearray): Photo taken via webcam.

        Returns:
            bool: A boolean if any usable faces are present.
        """
        try:
            with open(photo, 'rb') as image:
                response = self.client.detect_faces(
                    Image={
                        'Bytes': image.read()
                    },
                    Attributes=['ALL'])
                self.logger.info('Detected faces!')
                return response
        except ClientError as e:
            self.logger.error(e)
            raise(e)


class S3Helper(AbstractClientHelper):

    def __init__(self, aws_session=None, *args, **kwargs):
        super(S3Helper, self).__init__('s3', aws_session)

    def upload_file(self, file_name: str, bucket: str, object_name: str = None) -> bool:
        """ Uploads a file to an S3 bucket.

        Args:
            file_name (str): File to upload.
            bucket (str): S3 bucket name.
            object_name (str): S3 object name.

        Returns:
            bool: A boolean if the upload was successful.
        """
        if object_name is None:
            object_name = os.path.basename(file_name)

        # Upload the file
        try:
            _ = self.client.upload_file(file_name, bucket, object_name)
        except ClientError as e:
            self.logging.error(e)
            return False
        return True


class SecretsManagerHelper(AbstractClientHelper):

    def __init__(self, aws_session=None, *args, **kwargs):
        super(
            SecretsManagerHelper,
            self).__init__(
            'secretsmanager',
            aws_session)

    def get_secret(self, secret_arn: str) -> str:
        """ Retrieves the secret value from AWS Secrets Manager.

        Args:
            secret_arn (str): ARN of the secret to retrieve.

        Raises:
            DecryptionFailureException: Could not decrypt the secret.
            InternalServiceErrorException: Internal service error.
            InvalidParameterException: Invalid parameter.
            InvalidRequestException: Invalid request.
            ResourceNotFoundException: Resource not found.

        Returns:
            str: Secret object.
        """
        try:
            get_secret_value_response = self.client.get_secret_value(
                SecretId=secret_arn
            )
        except ClientError as error:
            if error.response['Error']['Code'] == 'DecryptionFailureException':
                raise error
            elif error.response['Error']['Code'] == 'InternalServiceErrorException':
                raise error
            elif error.response['Error']['Code'] == 'InvalidParameterException':
                raise error
            elif error.response['Error']['Code'] == 'InvalidRequestException':
                raise error
            elif error.response['Error']['Code'] == 'ResourceNotFoundException':
                raise error
        else:
            if 'SecretString' in get_secret_value_response:
                secret = get_secret_value_response['SecretString']
            else:
                secret = base64.b64decode(
                    get_secret_value_response['SecretBinary'])
            return json.loads(secret)


def main():
    secret_arn = os.environ.get('SECRET_ARN')
    secret = SecretsManagerHelper().get_secret(secret_arn)

    jgCollectionId = 'collection_bucket_name'
    jg_faces_bucket = 'faces_bucket_name'
    temporary_bucket = 'temporary_bucket_name'
    unknown_faces_bucket = 'unknown_faces_bucket_name'

    polly = PollyHelper()
    rekognition = RekognitionHelper()
    s3 = S3Helper()
    cam = cv2.VideoCapture(0)

    while True:
        ret, frame = cam.read()
        if not ret:
            logger.error("Failed to grab frame!")
            break
        cv2.imshow("Capture", frame)
        cv2.namedWindow("Capture", cv2.WINDOW_NORMAL)
        k = cv2.waitKey(1)
        if k % 256 == 27:
            # ESC pressed
            logger.info("Escape hit, closing!")
            break
        elif k % 256 == 32:
            # SPACE pressed
            date = get_current_date()
            epoch_time = int(time.time())
            photo = f"opencv_frame_{epoch_time}.png"
            # this is for performance improvements, as we don't need a full size image to detect faces
            resized_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            cv2.imwrite(photo, resized_frame)
            # this reads in the photo as grayscale, which is optimal for scoping individual faces via bounding boxes and passing them to search_faces_by_image
            image = cv2.imread(photo, 0)
            height, width = image.shape
            names = []
            face_number = 0
            detected_faces = rekognition.detect_faces(photo)
            if detected_faces['FaceDetails']:
                for faceDetail in detected_faces['FaceDetails']:
                    if faceDetail['Confidence'] >= 90:
                        bounding_box = faceDetail['BoundingBox']
                        cropped_image_name = crop_image_via_bounding_box(image, height, width, bounding_box, epoch_time, face_number)
                        face, name = rekognition.search_faces_by_image(cropped_image_name, jgCollectionId)
                        if face:
                            names.append(name)
                            write_to_climb_db(secret, face, date)
                            s3.upload_file(cropped_image_name, jg_faces_bucket, object_name="logged/" + cropped_image_name)
                        else:
                            s3.upload_file(cropped_image_name, unknown_faces_bucket, object_name=None)
                            logger.info(f"No face found in image, uploading to S3 bucket: {unknown_faces_bucket}")
                    face_number += 1
            else:
                polly.synthesize_speech(f"No faces found, please try again!")

            if len(names) > 1:
                polly.synthesize_speech(
                    'Your stairs have been logged ' + str(names)[1:-1] + 'and' + str(names)[-1])
                s3.upload_file(photo, temporary_bucket, object_name=None)
            elif len(names) == 1:
                polly.synthesize_speech(
                    'Your stairs have been logged ' + str(names))
                s3.upload_file(photo, temporary_bucket, object_name=None)

    cam.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
