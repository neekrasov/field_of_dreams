include .env
export

 .PHONY: run-bot
run-bot:
	poetry run python src/field_of_dreams/presentation/tgbot/main.py

 .PHONY: migrate-up
migrate-up:
	poetry run alembic -c src/field_of_dreams/config/alembic.ini upgrade head

 .PHONY: migrate-down
migrate-down:
	poetry run alembic -c src/field_of_dreams/config/alembic.ini downgrade $(revision)

 .PHONY: migrate-create
migrate-create:
	poetry run alembic -c src/field_of_dreams/config/alembic.ini revision --autogenerate -m $(name)

 .PHONY: migrate-history
migrate-history:
	poetry run alembic -c src/field_of_dreams/config/alembic.ini history

 .PHONY: migrate-stamp
migrate-stamp:
	poetry run alembic -c src/field_of_dreams/config/alembic.ini stamp $(revision)
