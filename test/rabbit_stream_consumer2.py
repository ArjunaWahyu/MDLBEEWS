import asyncio
import signal
from rstream import (
    AMQPMessage,
    Consumer,
    MessageContext,
    ConsumerOffsetSpecification,
    OffsetType
)
import json

async def main():
    STREAM_NAME = "hello-python-stream"
    STREAM_RETENTION = 5000000000
    
    consumer = Consumer(host="localhost", username="admin", password="password", load_balancer_mode=True)
    await consumer.create_stream(
        STREAM_NAME, 
        exists_ok=True, 
        arguments={
                "MaxLengthBytes": STREAM_RETENTION
            }
    )

    async def on_message(msg: AMQPMessage, message_context: MessageContext):
        stream = message_context.consumer.get_stream(message_context.subscriber_name)
        # message_decoded = msg.decode()
        # print(f"Got message: {message_decoded} from stream {stream}")
        # print(type(message_decoded))
        # json.loads(x.decode('utf-8'))
        data = json.loads(msg.decode('utf-8'))
        print(data)
        print(data['station'])

    await consumer.start()
    await consumer.subscribe(
        stream=STREAM_NAME,
        callback=on_message,
        offset_specification=ConsumerOffsetSpecification(OffsetType.NEXT, None),
    )
    await consumer.run()
    
    # Graceful shutdown
    async def shutdown():
        await consumer.stop()
        await consumer.close()
        print("Consumer stopped")
        
    for sig in [signal.SIGINT, signal.SIGTERM]:
        signal.signal(sig, lambda s, f: asyncio.create_task(shutdown()))
        
if __name__ == "__main__":
    asyncio.run(main())