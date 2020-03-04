"""
Calls the appropriate module to do storage tasks. At the moment there's only the S3 module to
choose from
"""

class Storage():
    def __init__(self, storage_provider):
        if storage_provider == 's3':
            from cstash.storage.s3 import S3
            self.storage_provider = S3()

    def search(self, bucket, filename, storage_provider=None):
        storage_provider = storage_provider or self.storage_provider
        return self.storage_provider.search(bucket, filename)

    def upload(self, bucket, filename, storage_provider=None):
        storage_provider = storage_provider or self.storage_provider
        return self.storage_provider.upload(bucket, filename)
