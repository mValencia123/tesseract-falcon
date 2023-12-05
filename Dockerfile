FROM ubuntu:latest

WORKDIR /usr/src/app

COPY . ./

RUN apt-get update -y
RUN apt-get install tesseract-ocr -y
RUN apt-get install tesseract-ocr-spa -y
RUN apt-get install python3 -y
RUN apt-get install python3-pip -y
RUN apt-get install poppler-utils -y
RUN pip3 install -r requirements.txt

EXPOSE 8000


CMD ["python3", "./manage.py"]