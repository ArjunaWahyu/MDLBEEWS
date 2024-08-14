# create code to connect to rabbit mq stream container username admin password password port 5672 and send message
import asyncio
from rstream import Producer
import json
import time

async def main():
    print("connecting to rabbit mq stream container")
    async with Producer(
        host="localhost",
        username="admin",
        password="password",
        load_balancer_mode=True
    ) as producer:

        print("creating stream")
        STREAM_NAME = "hello-python-stream"
        # 5GB
        STREAM_RETENTION = 5000000000

        try:
            print("creating stream")
            await producer.create_stream(
                STREAM_NAME, 
                exists_ok=True, 
                arguments={"MaxLengthBytes": STREAM_RETENTION}
            )
        except Exception as e:
            print(f"Error creating stream {STREAM_NAME}: {e}")

        data = dict(
            station="BBJI2",
            channel="BHZ",
            data=[0]*1000,
            timestamp=int(time.time())
        )
        print(data)
        # json.dumps(v).encode('utf-8')
        await producer.send(STREAM_NAME, json.dumps(data).encode('utf-8'))

if __name__ == "__main__":
    asyncio.run(main())