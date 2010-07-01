# Makefile for Linux Foundation Code Janitor
# Copyright 2010 Linux Foundation.

default: media/docs/index.html

media/docs/index.html: media/docs/index.html.base media/docs/index.html.addons \
  media/docs/index.html.footer
	cd media/docs && \
	  cat index.html.base index.html.addons index.html.footer > index.html

media/docs/index.html.addons: AUTHORS Changelog doc/License doc/Contributing
	cd media/docs && ./text-docs-to-html > index.html.addons

clean:
	cd media/docs && rm -f index.html index.html.addons

.PHONY: clean
