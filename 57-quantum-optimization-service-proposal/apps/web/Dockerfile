FROM node:22-bookworm-slim AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
ARG OPTIMIZATION_API_BASE=http://api:8057
ENV OPTIMIZATION_API_BASE=$OPTIMIZATION_API_BASE
RUN npm run build

FROM node:22-bookworm-slim
WORKDIR /app
ENV NODE_ENV=production OPTIMIZATION_API_BASE=http://api:8057
COPY --from=builder /app/package.json /app/package-lock.json ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
EXPOSE 3057
CMD ["node", "node_modules/next/dist/bin/next", "start", "--hostname", "0.0.0.0", "-p", "3057"]
