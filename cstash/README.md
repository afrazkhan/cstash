**NOTE: DO NOT USE, THIS IS A WORK IN PROGRESSS**

A zero-knowledge file syncing solution.

## Rationale

AWS and others offer encryption at rest with their object storage solutions, but it's necessary for keys to be held by them. Cstash encrypts using local keys before uploading objects to cloud storage.

Filenames are also obsfucated using `secrets.token_urlsafe`, and storing real filename mapping in a local database.

## Features

* Local encryption / decryption — keys never leave your machine
* Filenames are obsfucated too, with only the local DB and an encrypted copy in remote storage as a means of finding out which object is which file
* Able to keep arbitrary files on your machine in sync with remote storage
* Multiple encryption options and cloud providers
