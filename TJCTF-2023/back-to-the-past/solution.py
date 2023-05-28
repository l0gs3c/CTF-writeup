import jwt
token = "eyJ0eXAiOiAiSldUIiwgImFsZyI6ICJIUzI1NiJ9.eyJpZCI6ICIxYmViMzZhMC05MTJmLTRhMGMtOWIzMy1jOGY3Zjg4NmU2M2YiLCAidXNlcm5hbWUiOiAiYW9kaiIsICJ5ZWFyIjogIjE5NzEifQ.fpFZq5kYOQ1DgQv1nRodng4RvQQkn9u2HGIo5iq0MAM"
public_key = open("static/public_key.pem", "rb").read()
algorithm = "HS245"
payload = {
  "id": "1beb36a0-912f-4a0c-9b33-c8f7f886e63f",
  "username": "aodj",
  "year": "1969"
}

def en_func():
    print(jwt.encode(
        payload, public_key, algorithm="HS256"
    ))

def de_func():
	try:
		return jwt.decode(token.encode(), public_key, algorithms=["HS256", "RS256"])
	except:
		return None
def very():
	user = de_func()
	if user is None:
		print("user is none")
	else:
		print(user)
	if int(user["year"]) > 1970:
	    print("no flag")
	else:
		print("flag")

en_func()

