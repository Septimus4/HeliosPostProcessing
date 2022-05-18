FROM ubuntu:18.04

RUN apt-get update -y
RUN apt-get upgrade -y
#Required packages
RUN apt-get install -y python3-pip build-essential git python3

RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata
RUN apt-get update -y

#OpenCV Packages
RUN apt-get install 'ffmpeg'\
    'libsm6'\
    'libxext6'\
    'cmake'\
    'poppler-utils'  -y

RUN apt-get install -y python-rtree

#App install
WORKDIR usr/src/heliosia
COPY requirements.txt .

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY . .