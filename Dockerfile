FROM python:3.9
RUN mkdir /parser
COPY requirements.txt .
RUN pip install -r requirements.txt
WORKDIR /parser