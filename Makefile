# Makefile for Linux Foundation Code Janitor
# Copyright 2010 Linux Foundation.

default: janitor/media/docs/index.html janitor/janitor.sqlite README.txt

janitor/media/docs/index.html: janitor/media/docs/index.html.base \
  janitor/media/docs/index.html.addons janitor/media/docs/index.html.footer
	cd janitor/media/docs && \
	  cat index.html.base index.html.addons index.html.footer > index.html

janitor/media/docs/index.html.addons: AUTHORS Changelog doc/License \
  doc/Contributing
	cd janitor/media/docs && ./text-docs-to-html > index.html.addons

janitor/janitor.sqlite: janitor/search/models.py
	cd janitor && python manage.py syncdb --noinput

fixture_regen:
	(cd janitor && python manage.py dumpdata --format xml) | \
	  xmllint --format - > search/fixtures/initial_data.xml

README.txt: janitor/media/docs/index.html
	w3m -dump $< > $@

clean:
	cd janitor/media/docs && rm -f index.html index.html.addons
	rm -f janitor/janitor.sqlite
	rm -f README.txt

.PHONY: clean fixture_regen
