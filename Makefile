.PHONY: help coverage

REPORTS_CONTAINER ?= cashier_reports
COVERAGE_MIN ?= 95
COVERAGE_OMIT ?= tests/*

help:
	@printf "Available targets:\n"
	@printf "  help      Show this help message\n"
	@printf "  coverage  Run unit tests with coverage inside the %s container and fail below %s%%\n" "$(REPORTS_CONTAINER)" "$(COVERAGE_MIN)"

coverage:
	@docker ps --filter name=^$(REPORTS_CONTAINER)$$ --format '{{.Names}}' | grep -qx '$(REPORTS_CONTAINER)' || { echo 'Container $(REPORTS_CONTAINER) is not running. Start it with docker compose up -d reports.'; exit 1; }
	docker exec $(REPORTS_CONTAINER) sh -lc "uv run --with coverage python -m coverage run --omit='$(COVERAGE_OMIT)' -m unittest discover -s tests && uv run --with coverage python -m coverage report -m --omit='$(COVERAGE_OMIT)' --fail-under=$(COVERAGE_MIN)"