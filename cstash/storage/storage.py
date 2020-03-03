"""
Calls the appropriate module to do storage tasks. At the moment there's only the S3 module to
choose from
"""

class Search():
    def __init__(self):
        pass

    def search(self, bucket, filename, storage_provider):
        if storage_provider == 's3':
            from cstash.storage.s3 import S3
            s3 = S3()
            return s3.search(bucket=None, filename=None)
