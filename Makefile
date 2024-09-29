.PHONY: test
test:
	./manage.py test apps

.PHONY: dev
dev:
	.venv/bin/uvicorn --reload config.asgi:application

.PHONY: gunicorn
gunicorn:
	.venv/bin/gunicorn config.asgi:application -w 4 -k uvicorn.workers.UvicornWorker
