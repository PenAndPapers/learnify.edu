# --- Stage 1: Build Environment ---
# Upgraded to Node 22 Alpine for perfect environment parity
FROM node:22-alpine AS builder
WORKDIR /app

# Enable Corepack and prepare pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Copy dependency manifests to maximize Docker layer caching
COPY pnpm-lock.yaml package.json ./

# Fetch dependencies cleanly from the lockfile
RUN pnpm install --frozen-lockfile

# Copy the rest of your Nuxt 4 application code
COPY . .

# Generate production build artifacts via Nitro
RUN pnpm build

# --- Stage 2: Tiny Runtime Environment ---
# Match the runtime base image identically to Node 22
FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

# Copy only the highly optimized compiled output from the builder stage
COPY --from=builder /app/.output ./.output

EXPOSE 3000

# Run the standalone Nitro engine server
CMD ["node", ".output/server/index.mjs"]