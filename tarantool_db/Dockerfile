FROM ubuntu:22.04

WORKDIR /app

RUN apt-get update && apt upgrade -y
# fix tarantool install problem
RUN apt-get install -y tzdata \
    && ln -fs /usr/share/zoneinfo/Europe/Moscow /etc/localtime \
    && dpkg-reconfigure --frontend noninteractive tzdata

RUN apt-get install -y curl make cmake

RUN curl -L https://tarantool.io/release/3/installer.sh | bash \
    && apt-get update \
    && apt-get install -y tarantool \
    # fix tt rocks no LUA headers problem
    && apt-get install -y tarantool-dev \
    && apt-get install -y tt

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
