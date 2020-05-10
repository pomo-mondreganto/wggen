import subprocess


class WGKey:
    def __init__(self, public: str, private: str):
        self.public = public
        self.private = private

    @classmethod
    def generate(cls):
        private_key = cls._generate_private_key()
        public_key = cls._public_from_private(private_key)
        return cls(public=public_key, private=private_key)

    @staticmethod
    def _generate_private_key() -> str:
        return subprocess.check_output(['wg', 'genkey']).decode().strip()

    @staticmethod
    def _public_from_private(private: str) -> str:
        inp = private.encode()
        data = subprocess.check_output(['wg', 'pubkey'], input=inp).decode().strip()
        return data
