# Build the Possibilista Next.js frontend with the locked npm dependency tree.
FROM node:20-alpine AS build

WORKDIR /app
ARG BACKEND_INTERNAL_URL=http://backend:8000
ENV BACKEND_INTERNAL_URL=${BACKEND_INTERNAL_URL}

# Copy dependency manifests first so Docker can reuse the install layer.
COPY package.json package-lock.json ./
RUN npm ci

# Copy the frontend source and create the production build.
COPY . .
RUN npm run build

# Run the production Next.js server.
FROM node:20-alpine AS runtime

WORKDIR /app
ENV NODE_ENV=production

COPY package.json package-lock.json ./
RUN npm ci --omit=dev

COPY --from=build /app/.next ./.next

# Next.js production server listens on port 3000 by default.
EXPOSE 3000

CMD ["npm", "run", "start"]
