# This is a work in progress. The packages are installed to run the interactive simulator. Configuring Docker
# With X11 is delicate, so punting for now
FROM ubuntu:18.04
RUN set -x
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
RUN python3 examples/basic_usage.py