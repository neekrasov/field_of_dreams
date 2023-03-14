FROM base-image
WORKDIR /usr/src/migrations
COPY . ./

CMD make migrate-up