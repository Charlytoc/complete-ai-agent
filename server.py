import os
import json
from fastapi import FastAPI
from fastapi import WebSocket

from src.completions import create_completion_generator
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import RedirectResponse
# from starlette.exceptions import HTTPException
from dotenv import load_dotenv
from src.utils.print_in_color import print_in_color
# Import dotenv and load the .env file

from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
import logging
load_dotenv()
logger = logging.getLogger(__name__)

def reload():
    print("something printed in the beginning")
    print(os.getenv("ENVIRONMENT"))

app = FastAPI(on_startup=reload())

    
if not os.getenv("ENVIRONMENT") == "DEV":
    logger.info("Setting middleware to redirect HTTP to HTTPS")
    app.add_middleware(HTTPSRedirectMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origins=["*"],
)



@app.websocket("/message")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        data_dict = json.loads(data)
        print(data_dict)  # {'system_prompt': ..., 'prompt': ...}
        
        async def completion_callback(chunk):
            print_in_color(chunk.choices[0].delta.content, "yellow")
            message = {
                "event": "chunk",
                "content": chunk.choices[0].delta.content
            }
            await websocket.send_text(json.dumps(message))

        async def finish_completion_callback():
            message = {
                "event": "finish",
                "content": ""
            }
            await websocket.send_text(json.dumps(message))

        await create_completion_generator(data_dict["prompt"],data_dict["system_prompt"], completion_callback)
        await finish_completion_callback()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True, log_level="info")