FROM node:20-slim

WORKDIR /app

# instalar dependências
COPY package*.json ./
RUN npm install

# copiar código
COPY . .

# rodar o dev server
CMD ["npm", "run", "dev"]