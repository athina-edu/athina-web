FROM python:3.8
ENV PYTHONUNBUFFERED 1

ADD . /code
WORKDIR /code
RUN pip install pip
RUN pip install .
