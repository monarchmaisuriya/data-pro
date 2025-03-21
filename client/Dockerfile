# syntax=docker/dockerfile:1.4

# Stage 1: Development stage with hot-reload
FROM node:20-slim AS development

ENV COMPOSE_BAKE=true
WORKDIR /app

# Install pnpm globally and dependencies
RUN npm install -g pnpm

# Copy package.json and pnpm-lock.yaml for the dependencies
COPY package.json pnpm-lock.yaml ./
RUN pnpm install

# Copy source code
COPY . .

# Expose development port
EXPOSE 5173

# Start development server
CMD ["pnpm", "dev", "--host"]

# Stage 2: Build stage for creating optimized assets
FROM node:20-slim AS builder

ENV COMPOSE_BAKE=true
WORKDIR /app

# Install pnpm globally and dependencies
RUN npm install -g pnpm

# Copy package files and install dependencies
COPY package.json pnpm-lock.yaml ./
RUN pnpm install

# Copy source code and build
COPY . .
RUN pnpm build

# Stage 3: Production stage with Nginx
ENV COMPOSE_BAKE=true
FROM nginx:alpine AS production

# Copy the built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom nginx configuration if needed
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]