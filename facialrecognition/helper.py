import boto3
import logging
import sys


class AbstractHelper:
    def _filter_properties(self, properties: dict):
        valid_keys = [
            "region_name",
            "api_version",
            "use_ssl",
            "verify",
            "endpoint_url",
            "aws_access_key_id",
            "aws_secret_access_key",
            "aws_session_token",
            "config"]
        filtered_properties = properties.copy()
        for key in properties:
            if key not in valid_keys:
                del (filtered_properties[key])
        return filtered_properties

    def __init__(self, aws_session: boto3.Session = None, *args, **kwargs):
        if aws_session:
            self.session = aws_session
        else:
            self.session = boto3.Session(**kwargs)
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(logging.INFO)
        if not self._logger.hasHandlers():
            self._logger.addHandler(logging.StreamHandler(stream=sys.stdout))
        self._boto_properties = self._filter_properties(kwargs)

    def set_region(self, region_name):
        self.session.region_name = region_name

    @property
    def logger(self):
        return self._logger


class AbstractClientHelper(AbstractHelper):
    def __init__(self, client_type: str,
                 aws_session: boto3.Session = None, *args, **kwargs):
        super().__init__(aws_session, *args, **kwargs)
        self._client_type = client_type

    @property
    def client(self):
        if len(self._boto_properties) > 0:
            client_object = self.session.client(
                self._client_type, **self._boto_properties)
        else:
            client_object = self.session.client(self._client_type)
        return client_object


class AbstractResourceHelper(AbstractHelper):
    def __init__(self, resource_type: str,
                 aws_session: boto3.Session = None, *args, **kwargs):
        super().__init__(aws_session, *args, **kwargs)
        self._resource_type = resource_type

    @property
    def resource(self):
        if len(self._boto_properties) > 0:
            resource_object = self.session.resource(
                self._resource_type, **self._boto_properties)
        else:
            resource_object = self.session.resource(self._resource_type)
        return resource_object
