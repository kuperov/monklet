.PHONY: test
test:
	./manage.py test apps.projects.tests apps.pages.tests apps.users.tests
