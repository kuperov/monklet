.PHONY: test
test:
	./manage.py test apps

.PHONY: pw
pw:
	./manage.py test apps.projects.tests.test_projects

.PHONY: dev
dev:
	DEBUG=True .venv/bin/uvicorn --reload config.asgi:application --host 0.0.0.0 --port 8765

.PHONY: gunicorn
gunicorn:
	.venv/bin/gunicorn config.asgi:application -w 4 -k uvicorn.workers.UvicornWorker

.PHONY: run
run:
	.venv/bin/python3 manage.py runserver 0.0.0.0:8765

.PHONY: build
build:
	rm -rf staticfiles
	npm --prefix src run build:prod
	.venv/bin/python3 manage.py collectstatic

.PHONY: .venv
.venv: requirements.txt
	python3 -m venv .venv
	.venv/bin/python -m pip install -r requirements.txt
	sudo apt install libatk-bridge2.0-0 libxkbcommon0 libgbm1 libatspi2.0-0
	python -m playwright install

.PHONY: dump
dump:
	pg_dump -d monklet -F c -f snapshot.dump
