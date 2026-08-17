UV ?= uv
PYTEST_ARGS ?=
BUILD_ARGS ?=
ARM64_OUTPUT ?=

all: help

.PHONY: help
help: ## List all commands
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_-]+:.*?## / {printf "\033[36m%-26s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Tests

.PHONY: test
test: ## Run the default test suite (excludes SDL and stress tests)
	$(UV) run pytest -v $(PYTEST_ARGS)

.PHONY: tests
tests: test ## Alias for test

.PHONY: test-generator
test-generator: ## Run binding-generator tests
	$(UV) run pytest -v tests/generator $(PYTEST_ARGS)

.PHONY: test-runtime
test-runtime: ## Run binding runtime tests
	$(UV) run pytest -v tests/runtime $(PYTEST_ARGS)

.PHONY: test-cpython
test-cpython: ## Run MicroPythonOS-shaped CPython acceptance tests
	$(UV) run pytest -v tests/cpython $(PYTEST_ARGS)

.PHONY: test-integration
test-integration: ## Run integration tests that do not require SDL
	$(UV) run pytest -v -m "integration and not sdl" $(PYTEST_ARGS)

.PHONY: test-sdl
test-sdl: ## Run tests that require SDL and a display
	$(UV) run pytest -v -m sdl $(PYTEST_ARGS)

.PHONY: test-stress
test-stress: ## Run slow stress tests
	$(UV) run pytest -v -m stress $(PYTEST_ARGS)

.PHONY: test-acceptance
test-acceptance: ## Run acceptance tests
	$(UV) run pytest -v -m acceptance $(PYTEST_ARGS)

.PHONY: check-generated
check-generated: ## Check that generated bindings are up to date
	$(UV) run python -m builder.check_regeneration

# Binding generation

.PHONY: regenerate-py
regenerate-py: ## Regenerate the CPython binding
	$(UV) run python -m builder.regenerate py

.PHONY: regenerate-mpy
regenerate-mpy: ## Regenerate the MicroPython binding
	$(UV) run python -m builder.regenerate mpy

.PHONY: regenerate
regenerate: ## Regenerate both CPython and MicroPython bindings
	$(UV) run python -m builder.regenerate all

# Builds

.PHONY: build
build: ## Build the wheel and source distribution
	$(UV) build $(BUILD_ARGS)

.PHONY: build-wheel
build-wheel: ## Build a wheel
	$(UV) build --wheel $(BUILD_ARGS)

.PHONY: build-sdist
build-sdist: ## Build a source distribution
	$(UV) build --sdist $(BUILD_ARGS)

.PHONY: build-editable
build-editable: ## Rebuild and install the native extension in editable mode
	$(UV) pip install -e . --reinstall --no-deps

.PHONY: build-arm64-wheel
build-arm64-wheel: ## Build and validate a CPython 3.13 arm64 wheel
	./scripts/build_arm64_wheel.sh $(ARM64_OUTPUT)

# Native diagnostics

.PHONY: test-sanitizers
test-sanitizers: ## Run lifetime and integration tests with AddressSanitizer
	$(UV) run python -m builder.run_sanitizers

.PHONY: test-sanitizers-all
test-sanitizers-all: ## Run sanitizer tests with AddressSanitizer and UBSan
	$(UV) run python -m builder.run_sanitizers --sanitizers address,undefined
