# Frontend Dockerfile (Vite + React)
# Desarrollo con hot reload

FROM node:20-alpine

# Establecer directorio de trabajo
WORKDIR /app

# Copiar package.json y package-lock.json
COPY package*.json ./

# Instalar dependencias
RUN npm install

# Copiar el resto del código
COPY . .

# Exponer puerto del dev server de Vite
EXPOSE 5173

# Comando para iniciar Vite dev server
# --host 0.0.0.0 permite acceso desde fuera del contenedor
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
