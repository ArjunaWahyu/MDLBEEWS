import json
import asyncio
from threading import Thread
from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from kafka import KafkaConsumer
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

connected_clients = set()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception as e:
        print(f"Client disconnected: {e}")
    finally:
        connected_clients.remove(websocket)

def consume():
    consumer = KafkaConsumer(
        'trace_topic',
        # bootstrap_servers='kafka:9092',
        bootstrap_servers=['kafka1:9092', 'kafka2:9093', 'kafka3:9094'],
        group_id='api-server-group',
        auto_offset_reset='earliest',
        key_deserializer=lambda k: json.loads(k.decode('utf-8')),
        value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    )
    for message in consumer:
        data = message.value
        print(f"Key: {message.key}, Partition: {message.partition}, Station: {data['station']}, Channel: {data['channel']}")
        endpoint = 'waves-data'
        message_data = {endpoint: data}
        # Broadcasting message to all connected WebSocket clients
        asyncio.run(broadcast_message(message_data))

async def broadcast_message(message):
    clients_to_remove = []
    for client in connected_clients:
        try:
            await client.send_text(json.dumps(message))
            # print(f"Message sent to client: {message}")
        except Exception as e:
            print(f"Error sending message to client: {e}")
            clients_to_remove.append(client)
    # Remove clients that encountered errors
    for client in clients_to_remove:
        connected_clients.remove(client)

@app.get("/")
async def get():
    # run public/index.html
    return FileResponse("public/index.html")

if __name__ == "__main__":
    consumer_thread = Thread(target=consume)
    consumer_thread.start()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3333)
