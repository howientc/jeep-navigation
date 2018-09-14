# FROM frolvlad/alpine-python3
# # FROM masterandrey/docker-matplotlib
# RUN apk add py-matplotlib
# # RUN apk --no-cache --update-cache add gcc gfortran python python-dev py-pip build-base wget freetype-dev libpng-dev openblas-dev
# RUN ln -s /usr/include/locale.h /usr/include/xlocale.h

# RUN apk add --no-cache  python3-tkinter freetype-dev libpng-dev

# Below are the dependencies required for installing the common combination of numpy, scipy, pandas and matplotlib 
# in an Alpine based Docker image.
# FROM alpine:3.4
# RUN set -x
# RUN echo "http://dl-8.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories
# RUN apk --no-cache --update-cache add gcc gfortran python3 python3-dev  build-base wget freetype-dev libpng-dev openblas-dev
# RUN ln -s /usr/include/locale.h /usr/include/xlocale.h
# RUN pip3 install numpy matplotlib
# RUN pip3 install --no-cache-dir PyDispatcher


FROM ubuntu:18.04 as builder
RUN set -x
# These are build dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
  python3 python3-pip python3-tk python3-setuptools 
RUN pip3 install numpy matplotlib PyDispatcher
ENV DISPLAY :0
#install 
WORKDIR /opt/
RUN mkdir -p /opt
ADD src /opt/src
ADD tests /opt/tests
ADD examples /opt/examples
RUN python3 examples/plot_path.py