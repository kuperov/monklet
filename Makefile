.PHONY: test
test:
	./manage.py test apps

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
