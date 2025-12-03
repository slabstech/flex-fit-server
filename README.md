Flex Fitness - Server


sudo apt-get install libpq-dev python3-dev gcc
pip install -r requirements.txt 

cd src
uvicorn main:app --reload


docker build -t dwani/flex-fit-api -f Dockerfile .