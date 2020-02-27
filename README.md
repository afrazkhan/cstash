Use S3 for storing encrypted objects, without trusting keys to AWS.

## Usage

    # Find 'filename'
    cstash search 'filename'
    
    # Retrieve and decrypt 'filename'
    cstash get 'full/path/to/filename'

    # Encrypt and store 'filename'
    cstash put 'full/path/to/filename'

## Design

* SQLite for key value mapping of hashed filenames to real filenames
* GPG for encryption / decryption before and after files are sent to S3

## Functionality

### Send and Receive Objects

For sending:

1. Take filename as argument to send, and lookup key in local DB

### Browse and Search Bucket
