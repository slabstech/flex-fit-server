QR code - attendance management


pip install -r requirements.txt

uvicorn main:app --host 0.0.0.0 --port 8000


http://your-ip:8000/api/today-code



http://your-ip:8000/qr-image

http://your-ip:8000/

http://your-ip:8000/today-qr


http://localhost:8000/add-test-students



# 1. Clone / go into your project folder
cd attendance-server

# 2. Build and start (first time)
docker compose up --build -d

# 3. Subsequent runs (just start)
docker compose up -d