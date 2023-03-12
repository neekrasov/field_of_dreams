include .env
export


ALEMBIC:=src/field_of_dreams/config/alembic.ini
PRESENTATION:=src/field_of_dreams/presentation/

 .PHONY: run-amqp
run-amqp:
	poetry run python $(PRESENTATION)amqp/main.py

 .PHONY: run-bot
run-bot:
	poetry run python $(PRESENTATION)tgbot/main.py

 .PHONY: run-api
run-api:
	poetry run python $(PRESENTATION)api/main.py

 .PHONY: migrate-up
migrate-up:
	poetry run alembic -c $(ALEMBIC) upgrade head

 .PHONY: migrate-down
migrate-down:
	poetry run alembic -c $(ALEMBIC) downgrade $(revision)

 .PHONY: migrate-create
migrate-create:
	poetry run alembic -c $(ALEMBIC) revision --autogenerate -m $(name)

 .PHONY: migrate-history
migrate-history:
	poetry run alembic -c $(ALEMBIC) history

 .PHONY: migrate-stamp
migrate-stamp:
	poetry run alembic -c $(ALEMBIC) stamp $(revision)
