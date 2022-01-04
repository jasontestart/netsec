# Is the provided plaintext password pwned?
# Uses v3 of the PwnedPassword API
# https://haveibeenpwned.com/API/v3#PwnedPasswords
import requests
import hashlib

def is_compromised(plaintext):
    api = "https://api.pwnedpasswords.com/range/"
    password = plaintext.encode("utf-8")
    full_hash = hashlib.sha1(password).hexdigest().upper()

    prefix = full_hash[:5]
    uri = api + prefix
    req = requests.get(uri)
    # If production, I would throw an exception and leave it to the caller on how to handle.
    if not req.status_code == 200:
        print(f"ERROR: HTTP Satus Code {req.status_code}. See https://haveibeenpwned.com/API/v3#ResponseCodes")
        # Fail open
        return False

    suffix = full_hash[5:]
    # Suffixes are surrounded by LFs and colons
    if suffix in req.text:
        return True

    return False

if __name__ == '__main__':
    import sys
    if not len(sys.argv) == 2:
        print(f"Usage: {sys.argv[0]} <password>")
        quit()

    answer = is_compromised(sys.argv[1])
    if answer:
        print("compromised")
    else:
        print("not compromised")
