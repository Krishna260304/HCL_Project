FROM node:24-bookworm-slim AS build

WORKDIR /app

RUN corepack enable && corepack prepare pnpm@10.12.1 --activate

COPY . .

RUN pnpm install --no-frozen-lockfile

ENV NODE_ENV=production

ENV PORT=8084

ENV BASE_PATH=/

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
  '  location /health {' \
  '    return 200 "healthy\n";' \
  '    add_header Content-Type text/plain;' \
  '  }' \
  '  location / {' \
  '    try_files $uri $uri/ /index.html;' \
  '  }' \
  '}' \
  > /etc/nginx/conf.d/default.conf

EXPOSE 8084

CMD ["nginx", "-g", "daemon off;"]
