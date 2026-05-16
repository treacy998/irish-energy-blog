ROOT     := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
PYTHON   := $(ROOT)venv/bin/python
HUGO     := $(HOME)/.local/bin/hugo
SITE_DIR := $(ROOT)site

.PHONY: help run preview publish

help:
	@echo ""
	@echo "  make run       Generate charts and scaffold today's post"
	@echo "  make preview   Start local Hugo server at http://localhost:1313"
	@echo "  make publish   Commit and push (will ask for a commit message)"
	@echo ""

run:
	@cd $(ROOT) && $(PYTHON) pipeline/run_daily.py

preview:
	@cd $(SITE_DIR) && $(HUGO) server -D

publish:
	@cd $(ROOT) && read -p "Commit message: " msg && \
	git add . && \
	git commit -m "$$msg" && \
	git push
