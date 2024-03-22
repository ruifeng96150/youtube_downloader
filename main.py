import json
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from socketio import AsyncServer
from src.tools import *
from concurrent.futures import ThreadPoolExecutor


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
socketio = AsyncServer(async_mode="asgi", cors_allowed_origins="*")
output_path = "./output"
# 创建一个线程池，用于处理任务
executor = ThreadPoolExecutor()


def process_data(param):
    name = param["name"]
    # 进行实际的处理操作
    down_ytb_video(name, param["url"], output_path)
    print("download", name)
    return get_directory_info(output_path)


@app.get("/")
async def index():
    with open("templates/index.html", encoding="utf-8", errors="ignore") as file:
        return HTMLResponse(content=file.read(), status_code=200)


@socketio.event
async def message(sid, data):
    await socketio.emit("message", data)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        raw = await websocket.receive_text()
        try:
            print("get msg", raw)
            data = json.loads(raw)
            print("get data", data)
            result = {"action": data["action"], "data": ""}
            if data["action"] == "getlist":
                result["data"] = get_directory_info(output_path)
                await websocket.send_text(json.dumps(result))
            elif data["action"] == "download":
                result["action"] = "downloading"
                await websocket.send_text(json.dumps(result))

                # 启动一个新的线程处理任务
                future = executor.submit(process_data, data["data"])
                # 等待任务完成，并将结果发送给前端
                result["action"] = "downloaded"
                result["data"] = future.result()
                await websocket.send_text(json.dumps(result))
            else:
                await websocket.send_text(json.dumps(result))

        except Exception as e:
            print("get msg error", e)


if __name__ == "__main__":
    """
    uvicorn main:app --reload
    """
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
