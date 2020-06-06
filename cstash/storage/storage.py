"""
Calls the appropriate module to do storage tasks. At the moment there's only the S3 module to
choose from
"""

import logging
import cstash.libs.exceptions as exceptions
import cstash.libs.helpers as helpers
import os

class Storage():
    def __init__(self, storage_provider, s3_access_key_id, s3_secret_access_key, log_level="ERROR", s3_endpoint_url=None):
        if storage_provider == 's3':
            from cstash.storage.s3 import S3
            self.storage_provider = S3(
                s3_endpoint_url=s3_endpoint_url,
                log_level=log_level,
                s3_access_key_id=s3_access_key_id,
                s3_secret_access_key=s3_secret_access_key
            )

    def search(self, bucket, filename, storage_provider=None):
        """
        Search [bucket] with [storage_provider] for [filename]

        * If [bucket] is None, then only return a listing of all buckets
        * If [filename] is not None, then return matching objects, otherwise return all objects
        """

        storage_provider = storage_provider or self.storage_provider
        return self.storage_provider.search(bucket, filename)

    def upload(self, bucket, filename, storage_provider=None):
        """
        Make calls to [storage_provider] to upload [filename] to [bucket]

        Return True for success, False for failure
        """

        storage_provider = storage_provider or self.storage_provider
        if self.storage_provider.bucket_exists(bucket) is False:
            raise exceptions.CstashCriticalException(message="Couldn't upload to bucket")

        logging.info("Uploading {} to {}".format(filename, bucket))
        return self.storage_provider.upload(bucket, filename)

    def download(self, bucket, filename, destination=None, storage_provider=None):
        """
        Make calls to [storage_provider] to fetch [filename] from [bucket],
        and store it on disk at [destination]. [destination] defaults to the current
        working directory and [filename], or if a directory is given, then
        [destination]/[filename].

        Return [destination] for success, or raise a CstashCriticalException on failure
        """

        if destination is not None and os.path.isdir(destination):
            destination = f"{destination}/{filename}"

        destination = destination or f"{os.getcwd()}/{filename}"
        destination = helpers.clear_path(destination)

        storage_provider = storage_provider or self.storage_provider

        downloaded_object = self.storage_provider.download(bucket, filename, destination)

        if downloaded_object is False:
            raise exceptions.CstashCriticalException(message="Couldn't download {} from {}".format(filename, storage_provider))

        return downloaded_object
