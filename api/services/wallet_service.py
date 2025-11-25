import ecdsa
import base64
from pydantic import BaseModel

class Wallet(BaseModel):
    private_key: str
    public_key: str
    address: str

def generate_wallet():
    # SECP256k1 is the curve used by Bitcoin
    sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
    vk = sk.verifying_key

    private_key = sk.to_string().hex()
    public_key = vk.to_string().hex()

    # Simple address generation (hash of public key)
    # In real Bitcoin: Base58Check(RIPEMD160(SHA256(PubKey)))
    # Here simplified to hex of pubkey for brevity, or we can do a simple hash
    import hashlib
    address = hashlib.sha256(public_key.encode()).hexdigest()[:40] # Take first 40 chars

    return Wallet(private_key=private_key, public_key=public_key, address=address)

def sign_message(private_key_hex: str, message: str) -> str:
    sk = ecdsa.SigningKey.from_string(bytes.fromhex(private_key_hex), curve=ecdsa.SECP256k1)
    signature = sk.sign(message.encode())
    return signature.hex()

def verify_signature(public_key_hex: str, message: str, signature_hex: str) -> bool:
    try:
        vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(public_key_hex), curve=ecdsa.SECP256k1)
        return vk.verify(bytes.fromhex(signature_hex), message.encode())
    except:
        return False
