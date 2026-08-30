FROM node:24-bookworm-slim AS build

WORKDIR /app

RUN corepack enable && corepack prepare pnpm@10.12.1 --activate

COPY . .

RUN pnpm install --frozen-lockfile --ignore-scripts

ARG VITE_BACKEND_WS_URL
ARG VITE_BACKEND_HOST
ARG BASE_PATH=/
ENV NODE_ENV=production \
    PORT=8084 \
    BASE_PATH=${BASE_PATH} \
    VITE_BACKEND_WS_URL=${VITE_BACKEND_WS_URL} \
    VITE_BACKEND_HOST=${VITE_BACKEND_HOST}

RUN pnpm --filter @workspace/learnpath-ai run build

FROM nginx:1.29-alpine

COPY --from=build /app/artifacts/learnpath-ai/dist/public /usr/share/nginx/html

RUN printf '%s\n' \
  'server {' \
  '  listen 8084;' \
  '  listen [::]:8084;' \
  '  server_name _;' \
  '  root /usr/share/nginx/html;' \
  '  index index.html;' \
  '  access_log off;' \
  '  gzip on;' \
  '  gzip_comp_level 4;' \
  '  gzip_min_length 1024;' \
  '  gzip_types text/plain text/css application/javascript application/json image/svg+xml;' \
  '  location /health {' \
  '    return 200 "healthy\n";' \
  '    add_header Content-Type text/plain;' \
  '  }' \
  '  location /assets/ {' \
  '    expires 1y;' \
  '    add_header Cache-Control "public, immutable";' \
  '    try_files $uri =404;' \
  '  }' \
  '  location / {' \
  '    try_files $uri $uri/ /index.html;' \
  '  }' \
  '}' \
  > /etc/nginx/conf.d/default.conf

EXPOSE 8084

CMD ["nginx", "-g", "daemon off;"]
