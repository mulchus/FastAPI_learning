lint: ## Проверяет линтером код в репозитории
	docker compose run --rm editorconfig-checker
	docker compose run --rm py-linters flake8 /check/
	docker compose run --rm py-linters mypy /check/
	docker compose run --rm py-linters isort --check-only --settings-path /opt/linters/pyproject.toml /check/

test: ## Запускает автотесты
	docker compose run --rm test pytest
#
#makemigrations: ## Создаёт новые файлы миграций Django ORM
#	docker compose run --rm django ./manage.py makemigrations
#
#migrate: ## Применяет новые миграции Django ORM
#	docker compose run --rm django ./manage.py migrate

help: ## Отображает список доступных команд и их описания
	@echo "Cписок доступных команд:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

isort: ## Сортирует импорты в коде
ifdef file
	docker compose run --rm --user $(shell id -u):$(shell id -g) py-linters isort --sp /opt/linters/pyproject.toml $(file)
else
	docker compose run --rm --user $(shell id -u):$(shell id -g) py-linters isort --sp /opt/linters/pyproject.toml /check/
endif
