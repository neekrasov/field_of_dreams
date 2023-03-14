FROM base-image
WORKDIR /usr/src/amqp
COPY . ./

CMD export DOCKER=1 && make run-amqp