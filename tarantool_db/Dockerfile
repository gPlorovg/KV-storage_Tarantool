FROM ubuntu:20.04

WORKDIR /app

RUN apt-get update && apt upgrade -y

RUN apt-get -y install tarantool

RUN curl -L https://tarantool.io/release/3/installer.sh | bash

RUN apt-get -y install tt
RUN tt init

COPY ./instances.enabled ./instances.enabled

RUN tt build users_cluster
RUN tt build data_cluster

RUN tt start

RUN tt connect users_cluster:users_router-a-001
RUN vshard.router.bootstrap()
RUN \q

RUN tt connect data_cluster:data_router-a-001
RUN vshard.router.bootstrap()
RUN \q 

