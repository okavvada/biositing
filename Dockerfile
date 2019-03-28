FROM ubuntu:latest
MAINTAINER Olga Kavvada “okavvada@gmail.com"
RUN apt-get update && \
      apt-get -y install sudo

RUN sudo apt-get install -y git
RUN apt-get install -y python-pip python-dev build-essential
COPY . /app
WORKDIR /app
RUN pip install --upgrade pip
RUN apt-get install -y libspatialindex-dev
RUN pip install -r requirements.txt
RUN pip install git+git://github.com/geopandas/geopandas.git

ENTRYPOINT ["python"]
CMD ["app.py"]