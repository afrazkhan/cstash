**NOTE: DO NOT USE, THIS IS A WORK IN PROGRESSS**

A zero-knowledge file syncing solution.

## Rationale

When using [server side encryption](https://docs.aws.amazon.com/AmazonS3/latest/dev/ServerSideEncryptionCustomerKeys.html) with AWS S3, keys are sent as part of the upload call. The documentation states that Amazon "_removes the encryption key from memory_" after use. It also states that "_Server-side encryption encrypts only the object data, not object metadata_".

This leaves data in S3 vulnerable to both malicious intent, and potential incompitance.

Cstash encrypts files using local keys before uploading them to cloud storage. Filenames are also obsfucated using sha256, with a local database holding a map to the real filename (recovery is possible from an encrypted version stored along with the objects).

## Features

* Local encryption / decryption — keys never leave your machine
* Filenames are one way hashed using sha256, with only the local DB and an encrypted copy in remote storage as a means of finding out which object is which file
* Able to keep arbitrary files on your machine in sync with remote storage
* Multiple encryption options and cloud providers supported

## Instalation

Don't, it isn't ready yet.

## TODO

A lazy man's ticket list:

* Add option to backup database after stashing a file too
* Move db parameter to class initialisation instead of method calls for FilenamesDatabase()
* Use click() native file handling (maybe?):
  * https://click.palletsprojects.com/en/7.x/arguments/#file-arguments
  * https://click.palletsprojects.com/en/7.x/arguments/#file-path-arguments
* Implement `cstash delete local` and `cstash delete remote` for DB and storage operations, respectively
* Implement daemon
* Implement Python native encryption
* Implement Google Cloud storage
* Implement Digital Ocean storage
* Add `cstash fetch [filename] --destination` to override original the file path
