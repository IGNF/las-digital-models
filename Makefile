# Makefile to manage main tasks
# cf. https://blog.ianpreston.ca/conda/python/bash/2020/05/13/conda_envs.html#makefile

# Oneshell means I can run multiple lines in a recipe in the same shell, so I don't have to
# chain commands together with semicolon
.ONESHELL:

# --------------------
# Environment creation
# --------------------

# mamba env update also works when environment does not exist yet
install:
	mamba env update -n produits_derives_lidar -f environment.yml

# --------------------
# pip library creation
# --------------------

deploy: check
	twine upload --repository-url https://nexus.ign.fr/repository/pypi-lidarhd-hosted/ dist/*

check: dist/ign-mnx*.tar.gz
	twine check dist/*

dist/ign-mnx*.tar.gz:
	python -m build

build: clean
	python -m build

clean:
	rm -rf tmp
	rm -rf ign-mnx.egg-info
	rm -rf dist

# --------------------
# Tests
# --------------------

testing:
	python -m pytest -s \
	--log-cli-level=INFO --log-format="%(asctime)s %(levelname)s %(message)s" \
	--log-date-format="%Y-%m-%d %H:%M:%S"


# --------------------
# Docker
# --------------------

PROJECT_NAME=lidar_hd/produits_derives_lidar
VERSION=`python -m produits_derives_lidar.version`
REGISTRY=docker-registry.ign.fr

docker-build:
	docker build -t ${PROJECT_NAME}:${VERSION} -f Dockerfile .

docker-test:
	docker run --rm -it ${PROJECT_NAME}:${VERSION} python -m pytest -s

docker-remove:
	docker rmi -f `docker images | grep ${PROJECT_NAME} | tr -s ' ' | cut -d ' ' -f 3`

docker-deploy:
	docker login docker-registry.ign.fr -u svc_lidarhd
	docker tag ${PROJECT_NAME} ${REGISTRY}/${PROJECT_NAME}:${VERSION}
	docker push ${REGISTRY}/${PROJECT_NAME}:${VERSION}