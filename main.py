import pathlib
from typing import List

from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from PyPDF2 import PdfReader
import uvicorn

from src.conf import messages
from src.routes import notes, tags


# locate templates  # Integrating our templates with the engine.
templates = Jinja2Templates(directory="templates")


def get_txt_from_pdf(file: str) -> str:
    # creating a pdf reader object
    reader = PdfReader(file)
    text = ''

    for page in range(len(reader.pages)):
        text += reader.pages[page].extract_text()

    return text


app = FastAPI()

# app.include_router(tags.router, prefix='/api')
# app.include_router(notes.router, prefix='/api')
app.mount('/static', StaticFiles(directory='static'), name='static')
app.mount('/templates', StaticFiles(directory='templates'), name='templates')


# manager
class SocketManager:
    """
    SocketManager does:
    Connect users to websocket with the help of connect function.
    Disconnect/Remove users with disconnect function.
    Send messages to all the connected users with broadcast function.
    """
    def __init__(self):
        self.active_connections: List[(WebSocket, str)] = []

    async def connect(self, websocket: WebSocket, user: str):
        await websocket.accept()
        self.active_connections.append((websocket, user))

    def disconnect(self, websocket: WebSocket, user: str):
        self.active_connections.remove((websocket, user))

    async def broadcast(self, data):
        for connection in self.active_connections:
            await connection[0].send_json(data)    

manager = SocketManager()


@app.websocket("/api/chat")
async def chat(websocket: WebSocket):
    """
    websocket chat function does:
    Check to see if user is registered/authenticated by reading from browser cookie which we are going to set next.
    Connect user to websocket with connect() function of SocketManager.
    Get data from connected user and broadcast it to all connected users with websocket.receive_json() and broadcast() respectively.
    """
    sender = websocket.cookies.get("X-Authorization")
    if sender:
        await manager.connect(websocket, sender)
        response = {
            "sender": sender,
            "message": "got connected"
        }
        await manager.broadcast(response)
        try:
            while True:
                data = await websocket.receive_json()
                await manager.broadcast(data)
        except WebSocketDisconnect:
            manager.disconnect(websocket, sender)
            response['message'] = "left"
            await manager.broadcast(response)

"""
register and user endpoint does:
    Get user name from the frontend and validate (and parse) it with custom RegisterValidator pydantic model.
    Create a cookie on the browser with httponly set to True so that no script gets hold of it.
    Get user by reading browser cookie.
"""
@app.get("/api/current_user")
def get_user(request: Request):
    return request.cookies.get("X-Authorization")

class RegisterValidator(BaseModel):
    username: str

# class Response(BaseModel): # !!! ???? import Response and use instanse ?
#     status: int = 200
#     # headers: str
#     # cookies: str

# from fastapi.responses import HTMLResponse as Response
# from fastapi.responses import Response

@app.post("/api/register")
def register_user(user: RegisterValidator, response: Response):        # ? from fastapi.responses import HTMLResponse
    response.set_cookie(key="X-Authorization", value=user.username, httponly=True)
    # return True ## 

@app.post('/uploadfile/')
async def create_upload_file(file: UploadFile = File()) -> dict:
    pathlib.Path('uploads').mkdir(exist_ok=True)
    file_path = f'uploads/{file.filename}'

    file_type = file.filename.split('.')[-1].lower()
    if file_type == 'pdf':
        with open(file_path, 'wb') as f:
            f.write(await file.read())

        text = get_txt_from_pdf(file_path) # 'example.pdf'
        print(text)

        return {'file_text': text}  # file_path
    
    else:
        return {'file_text': f'Incorrect file-type. {file_type} not a PDF.'}  # file_path


# @app.get('/')
# def read_root() -> dict:
#     """
#     The read_root function returns a dictionary with the key 'message' and value of `WELCOME`

#     :return: A dictionary with the key 'message' and the value of `welcome`
#     :doc-author: Trelent
#     """
#     return {'message': messages.WELCOME}


# returning home and chat templates
@app.get("/")
def get_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/chat")
def get_chat(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
