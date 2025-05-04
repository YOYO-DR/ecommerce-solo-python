# Etapa 1: Construir la aplicación
FROM node:alpine
WORKDIR /app
COPY package*.json ./

# Considera usar 'npm ci' para instalaciones más rápidas y deterministas si tienes package-lock.json
RUN npm install
COPY . .
RUN npm run build

# === INICIO: Añadir wait-for-it ===
# Instalar dependencias (bash es recomendable para wait-for-it, curl para descargarlo)
RUN apk add --no-cache bash curl

# Descargar wait-for-it y hacerlo ejecutable
RUN curl -o /usr/local/bin/wait-for-it https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh \
    && chmod +x /usr/local/bin/wait-for-it
# === FIN: Añadir wait-for-it ===

COPY /app/dist /usr/share/nginx/html
# Configuración para manejar rutas de React Router
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY start /start
RUN chmod +x /start
EXPOSE 83

# No necesitas ENTRYPOINT si ya tienes el CMD por defecto de nginx
# Pero si quieres usar tu script /start para esperar y LUEGO lanzar nginx:
ENTRYPOINT ["/start"]
# Asegúrate que /start termine con 'exec nginx -g daemon off;' o similar
# Tu script /start actual parece correcto en ese sentido.