const { Kafka } = require('kafkajs');
const express = require("express");
const http = require("http");
const socketIo = require("socket.io");
const app = express();
const server = http.createServer(app);
const io = socketIo(server);
const cors = require("cors");

const initializeConsumer = async () => {
  console.log("Initializing Kafka consumer...");
  const kafka = new Kafka({
    clientId: 'api-server',
    brokers: ['kafka:9092'] // ganti dengan alamat broker Kafka Anda
  });

  const consumer = kafka.consumer({ groupId: 'api-server-group' });

  // Menghubungkan consumer
  await consumer.connect();

  // Subscribe ke topik dan baca dari awal (dari offset 0)
  // await consumer.subscribe({ topic: 'trace_topic', fromBeginning: true });
  await consumer.subscribe({ topic: 'trace_topic', fromBeginning: false });

  return consumer;
}

const initializeWebSocket = (consumer) => {
  console.log("Initializing WebSocket...");

  const clients = new Set();

  io.on("connection", (socket) => {
    console.log("A client connected.");
    clients.add(socket);

    socket.on("disconnect", () => {
      console.log("A client disconnected.");
      clients.delete(socket);
    });
  });

  consumer.run({
    eachMessage: async ({ topic, partition, message }) => {
      const data = JSON.parse(message.value);
      const key = JSON.parse(message.key);

      console.log(`Key: ${message.key},\tPartition ${partition},\tStation: ${data["station"]},\tChannel: ${data["channel"]}`);
      const endpoint = `waves-data`;

      for (let client of clients) {
        client.emit(endpoint, data);
      }
    },
  });
}

const main = async () => {
  app.use(cors());
  const consumer = await initializeConsumer();
  initializeWebSocket(consumer);

  app.get("/", (req, res) => {
    res.sendFile(__dirname + "/public/index.html");
  });

  server.listen(3333, () => {
    console.log("Server is running on port 3333");
  });
}

main();
