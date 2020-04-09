#!/usr/bin/env python3

import boto3
import logging
import cstash.libs.helpers as helpers
import os

class S3():

    def __init__(self, log_level=None):
        self.s3_client = boto3.client('s3')
        logging.getLogger().setLevel(log_level)

    def search(self, bucket=None, filename=None, s3_client=None):
        """
        Take [bucket], [filename], and [s3_client] for returning listings and:

        * If [bucket] is None, then only return a listing of all buckets
        * If [filename] is not None, then return matching objects, otherwise return all objects
        """

        s3_client = s3_client or self.s3_client

        if bucket == None:
            print("Returning listing of buckets, since you didn't supply a bucket (see --help)\n")
            return self.list_buckets()

        if filename == None:
            print("Returning a listing of the bucket {} only, since you did not supply an object to search for (see --help)\n".format(bucket))
            return self.get_objects(bucket, s3_client)

        all_objects = self.get_objects(bucket, s3_client)

        return [ s for s in all_objects if filename in s ]

    def list_buckets(self, s3_client=None):
        """ List all buckets in the account """

        s3_client = s3_client or self.s3_client

        return ([ bucket['Name'] for bucket in s3_client.list_buckets()['Buckets'] ])

    def bucket_exists(self, bucket, s3_client=None):
        """ Return True if [bucket] exists, False if it doesn't """

        s3_client = s3_client or self.s3_client

        try:
            s3_client.list_objects(Bucket=bucket, MaxKeys=1)
            return True
        except Exception as e:
            logging.error("Couldn't find bucket. Check access rights and whether the bucket actually exists: {}".format(e))
            return False

    def get_objects(self, bucket, s3_client=None):
        """ Take [bucket] and [s3_client], and return a list of all objects from [bucket] """

        all_objects = s3_client.list_objects_v2(Bucket=bucket)
        if 'Contents' in all_objects.keys():
            all_objects = [ k['Key'] for k in [ obj for obj in all_objects['Contents'] ]]
        else:
            all_objects = []

        return all_objects

    def upload(self, bucket, obj, s3_client=None):
        """ Upload [obj] to [bucket]. Return True for success, False for failure """

        s3_client = s3_client or self.s3_client
        transfer_config = boto3.s3.transfer.TransferConfig(multipart_threshold=1024, use_threads=True, max_concurrency=10)
        s3_transfer = boto3.s3.transfer.S3Transfer(client=s3_client, config=transfer_config)

        try:
            logging.debug("Uploading {} to {}".format(obj, bucket))
            s3_transfer.upload_file(obj, bucket, helpers.strip_path(obj)[1])

            return True

        except Exception as e:
            logging.error("Error uploading: {}".format(e))
            return False

    def download(self, bucket, obj, destination, s3_client=None):
        """
        Download [obj] from [bucket], and store on local disk at [destination]

        Return [destination] on success, False on failure
        """

        s3_client = s3_client or self.s3_client
        transfer_config = boto3.s3.transfer.TransferConfig(multipart_threshold=1024, use_threads=True, max_concurrency=10)
        s3_transfer = boto3.s3.transfer.S3Transfer(client=s3_client, config=transfer_config)

        try:
            logging.debug("Downloading {} to {}".format(obj, destination))
            s3_transfer.download_file(bucket, obj, destination)

            return destination

        except Exception as e:
            logging.error("Error downloading {}: {}".format(obj, e))
            return False
