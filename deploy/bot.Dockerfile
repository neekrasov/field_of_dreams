FROM base-image
WORKDIR /usr/src/bot
COPY . ./

CMD export DOCKER=1 && make run-bot