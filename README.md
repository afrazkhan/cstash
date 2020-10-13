**NOTE: This is in no way ready for consumption, and is a work in progress**

# Cstash

A zero-knowledge file syncing solution.

## Rationale

When using [server side encryption](https://docs.aws.amazon.com/AmazonS3/latest/dev/ServerSideEncryptionCustomerKeys.html) with AWS S3, keys are sent as part of the upload call. The documentation states that Amazon "_removes the encryption key from memory_" after use. It also states that "_Server-side encryption encrypts only the object data, not object metadata_".

This leaves data in S3 vulnerable to both malicious intent, and potential incompitance.

Cstash encrypts files using local keys before uploading them to cloud storage. Filenames are also obfuscated using SHA-256, with a local database holding a map to the real filename (recovery is possible from an encrypted version stored along with the objects).

## Features

* Local encryption / decryption — keys never leave your machine
* Filenames are one way hashed using sha256, with only the local DB and an encrypted copy in remote storage as a means of finding out which object is which file
* Able to keep arbitrary files on your machine in sync with remote storage — experimental
* Multiple encryption options and cloud providers supported

## Instalation

`pip install git+https://github.com/afrazkhan/cstash`

## Usage

The quickest way to get up and running is to initialise a new key and config with these two commands:

    cstash initialise
    cstash config write --bucket [BUCKET_NAME] --ask-for-s3-credentials

This will set you up with a configuration that uses a newly generated key stored at `$HOME/.cstash/keys/default` for encryption, and the bucket specified for storage, using AWS by default. See `cstash config write --help` for overriding default values, for example to use an available GPG key instead, or a different S3 compatible storage provider by specifing `--s3-endpoint-url`.

The CLI is fairly well documented with `--help`, but these are the basic examples for the lazy:

```sh
# Write configuration to use [GPG KEY ID] and [S3 BUCKET NAME]
cstash config -c gpg -s s3 -k [GPG KEY ID] -b [S3 BUCKET NAME]

# Encrypt a file to GPG and stash it away in S3. Note that you can override the values in your config by passing the options here again, allowing mixing and matching cryptographers, remote storage providers, keys, and buckets (--cryptographer, --storage-provider, --key, --bucket)
cstash stash [FILE TO STASH]

# Lookup stored files in the database. If no file is given to search for, all results are retrieved
cstash database search [PART OF FILENAME]

# Retrieve a file from remote storage. You can get the full path from the previous command above, if you've forgotten it
cstash fetch [FULL ORIGINAL PATH TO FILE]
```

There is also a daemon mode which will watch on-disk copies of previously uploaded files and re-upload them when they change — this is experimental and I recommend you don't try it:

```sh
cstash daemon start
```

## TODO

A lazy man's ticket list:

* Add option to backup database after stashing a file too
* Store temporary files in `~/.cstash/temp/` instead of `~/.cstash/`
* Implement `cstash database delete [entry]` and `cstash storage delete [object]`
* Implement Google Cloud storage
* Implement Digital Ocean storage
* Add `cstash fetch [filename] --destination` to override original the file path
