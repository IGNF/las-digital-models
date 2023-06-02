# Makefile to manage main tasks
# cf. https://blog.ianpreston.ca/conda/python/bash/2020/05/13/conda_envs.html#makefile

# Oneshell means I can run multiple lines in a recipe in the same shell, so I don't have to
# chain commands together with semicolon
.ONESHELL:

deploy: check
	twine upload --repository-url https://nexus.ign.fr/repository/pypi-lidarhd-hosted/ dist/*

check: dist/ign-mnx*.tar.gz 
	twine check dist/*

dist/ign-mnx*.tar.gz:
	python -m build

build: clean
	python -m build

testing:
	python -m pytest -s \
	--log-cli-level=INFO --log-format="%(asctime)s %(levelname)s %(message)s" \
	--log-date-format="%Y-%m-%d %H:%M:%S"

clean:
	rm -rf tmp
	rm -rf ign-mnx.egg-info
	rm -rf dist
