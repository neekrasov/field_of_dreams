FROM base-image
WORKDIR /usr/src/api
COPY . ./
CMD make run-api