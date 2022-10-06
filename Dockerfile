FROM python:3.9-slim-buster

RUN apt-get update && apt-get -y install \
    netcat gcc postgresql python3-pip git\
    g++ make cmake unzip libcurl4-openssl-dev\
    && apt-get clean

COPY ./app /usr/src/app
COPY ./requirements.txt /usr/src/

RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r /usr/src/requirements.txt
RUN pip3 install --no-cache-dir --target /usr/src awslambdaric

WORKDIR /usr/src
RUN apt-get -y install curl
RUN curl -Lo /usr/local/bin/aws-lambda-rie \
    https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie && \
    chmod +x /usr/local/bin/aws-lambda-rie

COPY entry_script.sh /usr/src
ENTRYPOINT [ "sh", "entry_script.sh" ]
CMD ["app.main.handler"]


# Legacy for EC2 deployment
# FROM python:3.9-slim-buster

# WORKDIR /usr/src

# ENV PYTHONUNBUFFERED 1
# ENV PYTHONDONTWRITEBYTECODE 1

# RUN apt-get update && apt-get -y install \
#     netcat gcc postgresql python3-pip git\
#     && apt-get clean

# RUN pip3 install --upgrade pip
# COPY ./requirements.txt /usr/src/
# RUN pip3 install --no-cache-dir -r requirements.txt

# COPY . /usr/src/

# CMD gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 app.main:app