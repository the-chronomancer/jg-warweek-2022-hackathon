# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# PDX-License-Identifier: MIT-0 (For details, see
# https://github.com/awsdocs/amazon-rekognition-developer-guide/blob/master/LICENSE-SAMPLECODE.)
import base64
import logging
from telnetlib import EC
import boto3
from botocore.exceptions import ClientError
import os
import json
import psycopg2


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    session = boto3.Session(profile_name='codewars')

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = session.client('s3')
    try:
        _ = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def add_faces_to_collection(bucket, photo, collection_id, external_image_id):
    session = boto3.Session(profile_name='codewars')
    client = session.client('rekognition')

    response = client.index_faces(CollectionId=collection_id,
                                  Image={
                                      'S3Object': {
                                          'Bucket': bucket,
                                          'Name': photo}},
                                  ExternalImageId=external_image_id,
                                  MaxFaces=1,
                                  QualityFilter="AUTO",
                                  DetectionAttributes=['ALL'])

    print('Results for ' + photo)
    print('Faces indexed:')
    for faceRecord in response['FaceRecords']:
        print('  Face ID: ' + faceRecord['Face']['FaceId'])
        print('  Location: {}'.format(faceRecord['Face']['BoundingBox']))

    print('Faces not indexed:')
    for unindexedFace in response['UnindexedFaces']:
        print(
            ' Location: {}'.format(
                unindexedFace['FaceDetail']['BoundingBox']))
        print(' Reasons:')
        for reason in unindexedFace['Reasons']:
            print('   ' + reason)
    return response


def get_secret():
    secret_name = "secret_arn"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.Session(profile_name='aws_profile')
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS key.
        # Depending on whether the secret is a string or binary, one of these
        # fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            secret = base64.b64decode(
                get_secret_value_response['SecretBinary'])
        return json.loads(secret)


def write_to_users_db(user_id, first_name, last_name, email):
    database = secret['dbInstanceIdentifier']
    user = secret['username']
    password = secret['password']
    host = secret['host_ip']
    port = secret['port']

    conn = psycopg2.connect(
        database=database,
        user=user,
        password=password,
        host=host,
        port=port)
    print("Database connection opened...")

    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (user_id, first_name, last_name, email) VALUES (%s, %s, %s, %s)",
        (user_id,
         first_name,
         last_name,
         email))
    conn.commit()
    print("Record inserted successfully...")
    conn.close()


secret = get_secret()


def main():

    collection_id = 'collection_bucket_name'
    bucket = 'faces_bucket_name'

    photo = 'firstletter_lastname_number.jpeg'
    first_name = 'first_name'
    last_name = 'last_name'

    email = first_name[0].lower() + last_name.lower() + '@jahnelgroup.com'
    external_image_id = first_name.lower() + '_' + last_name.lower()

    upload_file(photo, bucket)
    face_records = add_faces_to_collection(
        bucket, photo, collection_id, external_image_id)
    for faceRecord in face_records['FaceRecords']:
        user_id = faceRecord['Face']['FaceId']
    write_to_users_db(user_id, first_name, last_name, email)


if __name__ == "__main__":
    main()
