Flex Fitness - Server


sudo apt-get install libpq-dev python3-dev gcc
pip install -r requirements.txt 

cd src
uvicorn main:app --reload


docker build -t dwani/flex-fit-api -f Dockerfile .


--



curl -X POST "http://192.168.1.50:8000/add-test-students" -H "Content-Type: application/json"

curl -X POST "http://your-pc-ip:8000/add-student" \
     -H "Content-Type: application/json" \
     -d '{"student_id": "STD999", "name": "Sachin Kumar"}'