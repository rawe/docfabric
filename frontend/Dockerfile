FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine

ARG VERSION=dev
ARG COMPONENT_VERSION=0.0.0
ARG GIT_COMMIT=unknown
ARG BUILD_DATE=unknown

LABEL org.opencontainers.image.title="DocFabric UI" \
      org.opencontainers.image.description="Document infrastructure layer for AI-optimized access" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.revision="${GIT_COMMIT}" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.source="https://github.com/rawe/docfabric" \
      org.opencontainers.image.vendor="rawe" \
      org.opencontainers.image.licenses="MIT" \
      docfabric.component="ui" \
      docfabric.component.version="${COMPONENT_VERSION}"

COPY nginx.conf.template /etc/nginx/nginx.conf.template
COPY docker-entrypoint.sh /docker-entrypoint.d/40-envsubst-api-url.sh
RUN chmod +x /docker-entrypoint.d/40-envsubst-api-url.sh
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
