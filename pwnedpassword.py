# Is the provided plaintext password pwned?
# Uses v3 of the PwnedPassword API
# https://haveibeenpwned.com/API/v3#PwnedPasswords
import requests
import hashlib

# Returns True if pwned, otherwise returns False
def is_pwned(plaintext):
    return_val = False
    api = "https://api.pwnedpasswords.com/range/"
    password = plaintext.encode()
    full_hash = hashlib.sha1(password).hexdigest().upper()

    prefix = full_hash[:5]
    suffix = full_hash[5:]
    uri = f"{api}{prefix}"
    try:
        req = requests.get(uri)
    except requests.exceptions.ConnectionError as e:
        print("ERROR: Cannot connect to pwnedpassword api.")
        # Fail open
        return return_val

    if req.status_code != 200:
        print(f"ERROR: HTTP Satus Code {req.status_code}. See https://haveibeenpwned.com/API/v3#ResponseCodes")
    else:
        # Suffixes are surrounded by LFs and colons
        if suffix in req.text:
            return_val = True

    return return_val

if __name__ == '__main__':
    from getpass import getpass
    password = getpass("Enter a password:")
    status = ""
    if not is_pwned(password):
        status = "not "
    print(f"The password provided is {status}compromised.")
