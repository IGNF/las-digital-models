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
	mamba env update -n las_digital_models -f environment.yml

install-precommit:
	pre-commit install

# --------------------
# pip library creation
# --------------------

deploy: check
	twine upload  dist/*

check: dist/ign-las-digital-models*.tar.gz
	twine check dist/*

dist/ign-las-digital-models*.tar.gz:
	python -m build

build: clean
	python -m build

clean:
	rm -rf tmp
	rm -rf ign-las-digital-models.egg-info
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

REGISTRY=ghcr.io
NAMESPACE=ignf
IMAGE_NAME=las-digital-models
VERSION=`python -m las_digital_models.version`
FULL_IMAGE_NAME=${REGISTRY}/${NAMESPACE}/${IMAGE_NAME}:${VERSION}

docker-build:
	docker build -t ${IMAGE_NAME}:${VERSION} -f Dockerfile .

docker-build-pdal: clean
	docker build --build-arg GITHUB_REPOSITORY=alavenant/PDAL --build-arg GITHUB_SHA=master_28_05_25 -t ${IMAGE_NAME}:${VERSION} -f Dockerfile.pdal .

docker-test-pdal-version: clean
	docker run --rm  -t ${IMAGE_NAME}:${VERSION} pdal --version

docker-test-pdal-custom: clean
	docker run --rm  -t ${IMAGE_NAME}:${VERSION} python -m pytest -s -m "pdal_custom"
	
docker-test:
	docker run --rm ${IMAGE_NAME}:${VERSION} python -m pytest -s -m "not functional_test"

docker-remove:
	docker rmi -f `docker images | grep ${IMAGE_NAME}:${VERSION} | tr -s ' ' | cut -d ' ' -f 3`

docker-deploy:
	docker tag ${IMAGE_NAME}:${VERSION} ${FULL_IMAGE_NAME}
	docker push ${FULL_IMAGE_NAME}