# buatlah untuk menjalankan node js
FROM node:14

WORKDIR /app

COPY package*.json ./

RUN npm install

RUN npm install express http socket.io kafka-node body-parser cors @json2csv/plainjs kafkajs

COPY . .

EXPOSE 3333

CMD ["npm", "start"]