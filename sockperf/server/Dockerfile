FROM ubuntu:20.04

LABEL maintainer="dev@ballerina.io"
ENV DOCKER_API_VERSION 1.38 

ENV TZ=Asia/Dubai 

SHELL ["/bin/bash", "-c"]

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt update && apt install -y iputils-ping net-tools sockperf

WORKDIR /home/root

EXPOSE 11111

CMD sockperf server --tcp