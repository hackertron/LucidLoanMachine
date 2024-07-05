import dkim
import email
import sys

def verify_dkim_signature(email_file):
    try:
        # Open and read the email file
        with open(email_file, 'rb') as f:
            raw_email = f.read()

        # Parse the email
        parsed_email = email.message_from_bytes(raw_email)

        # Extract the headers and body
        headers = parsed_email.as_bytes().split(b'\r\n\r\n', 1)[0]
        body = parsed_email.get_payload(decode=True)

        # Verify DKIM signature
        if dkim.verify(raw_email):
            print("DKIM signature is valid.")
        else:
            print("DKIM signature is invalid.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python verify_dkim.py <path_to_email_file>")
        sys.exit(1)
    
    email_file = sys.argv[1]
    verify_dkim_signature(email_file)
