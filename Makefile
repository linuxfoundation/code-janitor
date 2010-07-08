# Makefile for Linux Foundation Code Janitor
# Copyright 2010 Linux Foundation.

default: media/docs/index.html janitor.sqlite README.txt

media/docs/index.html: media/docs/index.html.base media/docs/index.html.addons \
  media/docs/index.html.footer
	cd media/docs && \
	  cat index.html.base index.html.addons index.html.footer > index.html

media/docs/index.html.addons: AUTHORS Changelog doc/License doc/Contributing
	cd media/docs && ./text-docs-to-html > index.html.addons

janitor.sqlite: search/models.py
	python manage.py syncdb --noinput

fixture_regen:
	python manage.py dumpdata --format xml | xmllint --format - \
	  > search/fixtures/initial_data.xml

README.txt: media/docs/index.html
	w3m -dump $< > $@

clean:
	cd media/docs && rm -f index.html index.html.addons
	rm -f janitor.sqlite
	rm -f README.txt

.PHONY: clean fixture_regen
