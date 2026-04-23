PLUGIN_DIR := plugin
DIST_DIR := dist
PLUGIN_NAME := jakes-lesson-plan-magic.plugin
VENV_PYTHON := $(firstword $(wildcard .venv/bin/python .venv/Scripts/python.exe))
PYTHON ?= $(if $(VENV_PYTHON),$(VENV_PYTHON),python3)
PYTEST ?= $(PYTHON) -m pytest

.PHONY: test package smoke-package verify-release clean

test:
	$(PYTEST) $(PLUGIN_DIR)/tests

package:
	$(PYTHON) scripts/build_plugin.py --output $(DIST_DIR)/$(PLUGIN_NAME)

smoke-package: package
	$(PYTHON) scripts/smoke_packaged_plugin.py $(DIST_DIR)/$(PLUGIN_NAME)

verify-release: test smoke-package

clean:
	rm -rf $(DIST_DIR)
