FROM ubuntu:18.04

LABEL maintainer="dev@ballerina.io"
ENV DOCKER_API_VERSION 1.38 
COPY base-image/utils /home/root/utils/
COPY tests /home/root/ballerina-performance-cloud/tests/
COPY base-image/base-scenario.sh /home/root/
COPY base-image/configure-jmeter.sh /home/root/
COPY base-image/execute-tests.sh /home/root/
COPY base-image/init.sh /home/root/

ENV TZ=Asia/Dubai 
ENV CLUSTER_IP="123"

SHELL ["/bin/bash", "-c"]

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt update && apt install curl -y && apt install iputils-ping -y && apt install gpg -y&& apt install wget -y && apt install git -y

RUN sh /home/root/init.sh

WORKDIR /home/root

RUN source /etc/profile.d/10-perf-vm.sh

CMD source /etc/profile.d/10-perf-vm.sh && bash execute-tests.sh