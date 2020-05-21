**NOTE: This is in no way ready for consumption, and is a work in progress**

# Cstash

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

`pip install git+https://github.com/afrazkhan/cstash`

## Usage

The CLI is fairly well documented with `--help`, but these are the basic operations for the lazy:

```sh
# Set configuration so you don't need to pass options to the stash command every time
cstash config -c gpg -s s3 -k [GPG KEY ID] -b [S3 BUCKET NAME]

# Encrypt a file to GPG and stash it away in S3. Note that you can override the values in your config by passing the options here again, allowing mixing and matching cryptographers, remote storage providers, keys, and buckets (--cryptographer, --storage-provider, --key, --bucket)
cstash stash [FILE TO STASH]

# Lookup stored files in the database
cstash database search [PART OF FILENAME]

# Retrieve a file from remote storage
cstash fetch [FULL PATH TO FILE]
```

There is also a daemon mode which will watch on-disk copies of previously uploaded files and re-upload them when they change:

```sh
cstash daemon start
```

## TODO

A lazy man's ticket list:

* Add option to backup database after stashing a file too
* Store temporary files in `~/.cstash/temp/` instead of `~/.cstash/`
* `database search` should return a full listing on `--all` flag
* Implement `cstash database delete [entry]` and `cstash storage delete [object]`
* Implement Python native encryption
* Implement Google Cloud storage
* Implement Digital Ocean storage
* Add `cstash fetch [filename] --destination` to override original the file path
