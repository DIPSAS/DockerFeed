FROM python:3.8.1-buster

ARG VERSION=1.0.0
RUN pip install DockerFeed==${VERSION}

WORKDIR /charts

ENTRYPOINT ["dockerf"]