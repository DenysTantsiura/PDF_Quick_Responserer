from fastapi import FastAPI
import uvicorn

from src.conf import messages
from src.routes import notes, tags

app = FastAPI()

app.include_router(tags.router, prefix='/api')
app.include_router(notes.router, prefix='/api')

@app.get('/')
def read_root() -> dict:
    """
    The read_root function returns a dictionary with the key 'message' and value of `WELCOME`

    :return: A dictionary with the key 'message' and the value of `welcome`
    :doc-author: Trelent
    """
    return {'message': messages.WELCOME}


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
