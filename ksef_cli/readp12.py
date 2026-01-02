from cryptography.hazmat import backends
from cryptography.hazmat.primitives.serialization import pkcs12


def _load_pfx(file_path, password):
    with open(file_path, 'rb') as fp:
        return pkcs12.load_key_and_certificates(
            fp.read(),
            password.encode("utf8"),
            backends.default_backend()
        )


def read_cert(file_path: str, password: str) -> tuple[bytes, bytes]:
    p12pk, p12pc, _ = _load_pfx(file_path=file_path, password=password)
    return p12pk, p12pc
