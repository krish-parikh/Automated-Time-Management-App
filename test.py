from jose import jwt

# Define your payload
payload = {
    "sub": "1234567890",
    "name": "John Doe",
    "iat": 1516239022
}

# Define your secret key (you should keep this secret)
secret_key = "your-secret-key"

# Encode the payload into a JWT
token = jwt.encode(payload, secret_key, algorithm="HS256")

print("Encoded JWT:", token)

# Decode the JWT
decoded_payload = jwt.decode(token, secret_key, algorithms=["HS256"])

print("Decoded Payload:", decoded_payload)