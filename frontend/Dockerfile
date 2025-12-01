# Use the official Node.js image as the base image
FROM node:22-alpine

# Set the working directory inside the container
WORKDIR /app

# Instalar pnpm globalmente
RUN corepack enable && corepack prepare pnpm@latest --activate

# Copy package.json and package-lock.json to the working directory
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install

# Copy the rest of the application code to the working directory
COPY . .

# Expose the port Vite uses for development
EXPOSE 5173

# Command to start the Vite development server
CMD ["pnpm", "run", "dev", "--host"]