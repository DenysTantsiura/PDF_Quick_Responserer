import pathlib

from fastapi import FastAPI, File, UploadFile
from fastapi.staticfiles import StaticFiles
from PyPDF2 import PdfReader
import uvicorn

from src.conf import messages
from src.routes import notes, tags



def get_txt_from_pdf(file: str) -> str:
    # creating a pdf reader object
    reader = PdfReader(file)
    text = ''

    for page in range(len(reader.pages)):
        text += reader.pages[page].extract_text()

    return text


app = FastAPI()

app.include_router(tags.router, prefix='/api')
app.include_router(notes.router, prefix='/api')
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File()) -> dict:
    pathlib.Path("uploads").mkdir(exist_ok=True)
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    text = get_txt_from_pdf(file_path) # 'example.pdf'
    print(text)

    return {"file_text": text}  # file_path


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
