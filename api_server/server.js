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
    // brokers: ['kafka:9092'] // ganti dengan alamat broker Kafka Anda
    brokers: ['kafka1:9092', 'kafka2:9093', 'kafka3:9094'] // ganti dengan alamat broker Kafka Anda
  });

  const consumer = kafka.consumer({ groupId: 'api-server-group' });

  // Menghubungkan consumer
  await consumer.connect();

  // Subscribe ke topik dan baca dari awal (dari offset 0)
  // await consumer.subscribe({ topic: 'trace_topic', fromBeginning: true });
  await consumer.subscribe({ topic: 'trace_topic', fromBeginning: false });

  return consumer;
}

const initializeConsumer2 = async () => {
  console.log("Initializing Kafka consumer for loc_mag_topic...");
  const kafka = new Kafka({
    clientId: 'api-server2',
    // brokers: ['kafka:9092'] // ganti dengan alamat broker Kafka Anda
    brokers: ['kafka1:9092', 'kafka2:9093', 'kafka3:9094'] // ganti dengan alamat broker Kafka Anda
  });

  const consumer2 = kafka.consumer({ groupId: 'api-server-group2' });

  // Menghubungkan consumer
  await consumer2.connect();

  // Subscribe ke topik dan baca dari awal (dari offset 0)
  // await consumer2.subscribe({ topic: 'loc_mag_topic', fromBeginning: true });
  await consumer2.subscribe({ topic: 'result_loc_mag_topic', fromBeginning: false });
  return consumer2;
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
      // add current time unix timestamp with milisecond
      data['api_time'] = new Date().getTime();
      console.log(`Key: ${message.key},\tPartition ${partition},\tStation: ${data["station"]},\tChannel: ${data["channel"]}`);
      const endpoint = `waves-data`;

      for (let client of clients) {
        client.emit(endpoint, data);
      }
    },
  });
}

const initializeWebSocket2 = (consumer2) => {
  console.log("Initializing WebSocket for loc_mag_topic...");

  const clients = new Set();

  io.on("connection", (socket) => {
    console.log("A client connected for loc_mag_topic.");
    clients.add(socket);

    socket.on("disconnect", () => {
      console.log("A client disconnected from loc_mag_topic.");
      clients.delete(socket);
    });
  });

  consumer2.run({
    eachMessage: async ({ topic, partition, message }) => {
      const data = JSON.parse(message.value);
      const key = JSON.parse(message.key);
      // add current time unix timestamp with milisecond
      data['api_time'] = new Date().getTime();
      console.log(`Key: ${message.key},\tPartition ${partition},\tStation: ${data["station"]},\tChannel: ${data["channel"]}\tloc_mag: ${data["predictions_loc_mag"]}`);
      const endpoint = `loc-mag-data`;

      for (let client of clients) {
        client.emit(endpoint, data);
      }
    },
  });
}

const main = async () => {
  app.use(cors());
  const consumer = await initializeConsumer();
  const consumer2 = await initializeConsumer2();
  initializeWebSocket(consumer);
  initializeWebSocket2(consumer2);

  app.get("/", (req, res) => {
    res.sendFile(__dirname + "/public/index.html");
  });

  server.listen(3333, () => {
    console.log("Server is running on port 3333");
  });
}

main();
