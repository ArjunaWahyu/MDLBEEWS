# create simple fastapi app
from fastapi import FastAPI

app = FastAPI()

@app.post("/trace")
async def trace(data: dict):
    print(data)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)