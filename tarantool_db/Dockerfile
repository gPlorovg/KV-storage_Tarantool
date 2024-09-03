FROM ubuntu:22.04

WORKDIR /app

RUN apt-get update && apt upgrade -y
# fix tarantool install problem
RUN apt-get install -y tzdata \
    && ln -fs /usr/share/zoneinfo/Europe/Moscow /etc/localtime \
    && dpkg-reconfigure --frontend noninteractive tzdata

RUN apt-get install -y curl

# fix crud install problem
RUN apt-get install -y cmake

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

EXPOSE 3049

CMD ["tt", "start"]
