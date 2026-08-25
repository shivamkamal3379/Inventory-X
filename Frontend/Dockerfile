# syntax=docker/dockerfile:1

# --- Stage 1: build the static bundle ---------------------------------------- #
FROM node:22-alpine AS builder

WORKDIR /app

# npm ci needs the lockfile and installs exactly what it pins.
COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Vite inlines env vars at build time, so the API base URL is baked in here
# rather than read at runtime. Override with --build-arg when the API lives on
# a different origin than the site.
ARG VITE_API_BASE_URL=/api
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build


# --- Stage 2: serve ---------------------------------------------------------- #
FROM nginx:1.27-alpine AS runtime

RUN rm -rf /usr/share/nginx/html/*
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -qO- http://127.0.0.1/healthz >/dev/null || exit 1

CMD ["nginx", "-g", "daemon off;"]
