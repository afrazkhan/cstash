"""
Calls the appropriate module to do storage tasks. At the moment there's only the S3 module to
choose from
"""

import logging
import cstash.libs.exceptions as exceptions
import cstash.libs.helpers as helpers

class Storage():
    def __init__(self, storage_provider, log_level):
        if storage_provider == 's3':
            from cstash.storage.s3 import S3
            self.storage_provider = S3(log_level)
            helpers.set_logger(log_level)

    def search(self, bucket, filename, storage_provider=None):
        """
        Search [bucket] with [storage_provider] for [filename.

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

    def download(self, bucket, filename, destination, storage_provider=None):
        """
        Make calls to [storage_provider] to fetch [filename] from [bucket],
        and store it on disk at [destination]. [destination] defaults to the current
        working directory

        Return [destination] for success, and False for failure
        """

        storage_provider = storage_provider or self.storage_provider

        return self.storage_provider.download(bucket, filename, destination)
