PLUGIN_DIR := plugin
DIST_DIR := dist
PLUGIN_NAME := jakes-lesson-plan-magic.plugin
PYTHON ?= python3
PYTEST ?= $(PYTHON) -m pytest

.PHONY: test package clean sync-license

test:
	$(PYTEST) $(PLUGIN_DIR)/tests

sync-license:
	cp LICENSE $(PLUGIN_DIR)/LICENSE

package: sync-license
	mkdir -p $(DIST_DIR)
	rm -f $(DIST_DIR)/$(PLUGIN_NAME)
	cd $(PLUGIN_DIR) && zip -qr ../$(DIST_DIR)/$(PLUGIN_NAME) . \
		-x '.claude' '.claude/*' '.claude/**' \
		-x '.DS_Store' '*/.DS_Store' \
		-x '.coverage' \
		-x '.pytest_cache' '.pytest_cache/*' '.pytest_cache/**' \
		-x 'tests' 'tests/*' 'tests/**' \
		-x '__pycache__' '__pycache__/*' '__pycache__/**' \
		-x '*.pyc'

clean:
	rm -rf $(DIST_DIR)
