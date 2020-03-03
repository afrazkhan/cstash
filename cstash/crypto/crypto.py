"""
Calls the appropriate module to do encryption. At the moment it only does GnuPG
"""

class Encryption():
    def __init__(self, cstash_directory, cryptographer):
        if cryptographer is 'gpg':
            from cstash.crypto.gpg import GPG
            gpg = GPG()
            gpg.encrypt()
