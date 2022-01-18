FROM ballerina/jmeter_container:latest
LABEL maintainer="dev@ballerina.io"

RUN apt update -y && apt install bc -y

RUN useradd -m ballerina && echo "ballerina:ballerina" | chpasswd && adduser ballerina sudo
WORKDIR /home/ballerina
RUN echo "ballerina ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
USER ballerina

SHELL ["/bin/bash", "-c"]

COPY --chown=ballerina execute-tests.sh /home/ballerina/setup/ 

CMD bash /home/ballerina/setup/execute-tests.sh