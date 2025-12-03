
Register user

curl -X POST http://localhost:8000/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "gymbro", "email": "gym@example.com", "password": "secret123"}'

  Login

  curl -X POST http://localhost:8000/login \
  -d "username=gym@example.com&password=secret123" \
  -H "Content-Type: application/x-www-form-urlencoded"

  