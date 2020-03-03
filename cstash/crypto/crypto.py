"""
Calls the appropriate module to do encryption. At the moment it only does GnuPG
"""

class Encryption():
    def __init__(self, cstash_directory, cryptographer, log_level):
        if cryptographer is 'gpg':
            self.log_level = log_level
            from cstash.crypto.gpg import GPG
            self.encryptor = GPG(log_level)

        self.cstash_directory = cstash_directory

    def store_filename(self, filename):
        from cstash.crypto.filenames import Filenames
        Filenames(self.cstash_directory, self.log_level).store(filename)

    def encrypt(self, filename):
        self.store_filename(filename)

        self.encryptor.encrypt(filename)
