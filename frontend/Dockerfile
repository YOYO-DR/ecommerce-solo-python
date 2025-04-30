# Etapa 1: Construir la aplicación
FROM node:alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Etapa 2: Servir los archivos estáticos con Nginx
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
# Configuración para manejar rutas de React Router
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 83
CMD ["nginx", "-g", "daemon off;"]