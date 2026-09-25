FROM node:20-alpine

WORKDIR /app
COPY package*.json ./
RUN npm install --omit=dev
COPY app.js .

EXPOSE 5003
CMD ["npm", "start"]
