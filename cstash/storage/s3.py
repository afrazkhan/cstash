#!/usr/bin/env python3

import boto3

class S3():

    def __init__(self):
        self.s3_client = boto3.client('s3')

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
            print("Returning a listing of {} only, since you did not supply an object to search for (see --help)\n")
            return self.get_objects(bucket, s3_client)

        all_objects = self.get_objects(bucket, s3_client)
        return [ s for s in all_objects if filename in s ]

    def list_buckets(self, s3_client=None):
        """ List all buckets in the account """

        s3_client = s3_client or self.s3_client

        return ([ b['Name'] for b in s3_client.list_buckets()['Buckets'] ])

    def get_objects(self, bucket, s3_client=None):
        """ Take [bucket] and [s3_client], and return a list of all objects from [bucket] """

        all_objects = s3_client.list_objects_v2(Bucket=bucket)
        all_objects = [ k['Key'] for k in [ obj for obj in all_objects['Contents'] ]]

        return all_objects
