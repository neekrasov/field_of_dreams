FROM python:3.11.0
WORKDIR /usr/src/amqp

ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VIRTUALENVS_CREATE=false

COPY pyproject.toml poetry.lock ./

RUN pip install --upgrade pip
RUN pip install poetry
RUN poetry install --without dev --no-root
RUN poetry config virtualenvs.create false

COPY . ./

CMD export DOCKER=1 && make run-amqp