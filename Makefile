.PHONY: help release release-server release-ui _check-version

REGISTRY ?= ghcr.io/rawe
IMAGE_SERVER := $(REGISTRY)/docfabric-server
IMAGE_UI := $(REGISTRY)/docfabric-ui

GIT_COMMIT := $(shell git rev-parse --short HEAD 2>/dev/null || echo "unknown")
BUILD_DATE := $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")

SERVER_VERSION := $(shell grep -m1 'version' backend/pyproject.toml | cut -d'"' -f2)
UI_VERSION := $(shell grep -m1 '"version"' frontend/package.json | cut -d'"' -f4)

help:
	@echo "DocFabric — Container Image Release"
	@echo ""
	@echo "Available commands:"
	@echo "  make release VERSION=x.y.z               - Build all release images"
	@echo "  make release VERSION=x.y.z PUSH=true     - Build and push to registry"
	@echo "  make release-server VERSION=x.y.z        - Build server image only"
	@echo "  make release-ui VERSION=x.y.z            - Build UI image only"

release: _check-version release-server release-ui
	@echo "Release $(VERSION) complete!"
	@echo "Images built: $(IMAGE_SERVER):$(VERSION) / $(IMAGE_UI):$(VERSION)"
ifdef PUSH
	@echo "Images pushed to $(REGISTRY)"
else
	@echo "To push: make release VERSION=$(VERSION) PUSH=true"
endif

_check-version:
ifndef VERSION
	$(error VERSION is required. Usage: make release VERSION=1.0.0)
endif

release-server: _check-version
	@echo "Building $(IMAGE_SERVER):$(VERSION)..."
	@echo "  Component version: $(SERVER_VERSION)"
	@echo "  Git commit: $(GIT_COMMIT)"
	docker build \
		--build-arg VERSION=$(VERSION) \
		--build-arg COMPONENT_VERSION=$(SERVER_VERSION) \
		--build-arg GIT_COMMIT=$(GIT_COMMIT) \
		--build-arg BUILD_DATE=$(BUILD_DATE) \
		-t $(IMAGE_SERVER):$(VERSION) \
		-t $(IMAGE_SERVER):latest \
		-f backend/Dockerfile \
		backend
ifdef PUSH
	docker push $(IMAGE_SERVER):$(VERSION)
	docker push $(IMAGE_SERVER):latest
endif

release-ui: _check-version
	@echo "Building $(IMAGE_UI):$(VERSION)..."
	@echo "  Component version: $(UI_VERSION)"
	@echo "  Git commit: $(GIT_COMMIT)"
	docker build \
		--build-arg VERSION=$(VERSION) \
		--build-arg COMPONENT_VERSION=$(UI_VERSION) \
		--build-arg GIT_COMMIT=$(GIT_COMMIT) \
		--build-arg BUILD_DATE=$(BUILD_DATE) \
		-t $(IMAGE_UI):$(VERSION) \
		-t $(IMAGE_UI):latest \
		-f frontend/Dockerfile \
		frontend
ifdef PUSH
	docker push $(IMAGE_UI):$(VERSION)
	docker push $(IMAGE_UI):latest
endif
