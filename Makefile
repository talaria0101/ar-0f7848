.PHONY: providers probe reports test all

all: providers probe reports test

providers:
	python3 scripts/build_providers.py

probe:
	python3 scripts/probe.py

reports:
	python3 scripts/build_reports.py

test:
	python3 -W error scripts/test_facts.py -v
