.PHONY: test
test:
	./manage.py test apps.projects.tests apps.projects.pages apps.projects.users
