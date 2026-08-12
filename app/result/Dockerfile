# Use the current Node.js LTS runtime.
FROM node:24-slim

# Install only the runtime tools we need.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl tini \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/local/app

# Copy dependency manifests first so Docker can cache npm installs.
COPY package*.json ./

# Install exactly what is pinned in package-lock.json.
RUN npm ci --omit=dev \
    && npm cache clean --force

# Copy the application source.
COPY . .

# Run the service on a non-privileged port.
ENV PORT=8080

EXPOSE 8080

# Use the non-root user provided by the official Node image.
USER node

ENTRYPOINT ["/usr/bin/tini", "--"]

CMD ["node", "server.js"]
