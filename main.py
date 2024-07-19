from typing import Optional
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from modules.supabase.helpers import upload_file
from modules.masking import detect_and_mask_eyes
import os

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_home():
    return "eye-mask-generator server is running"


@app.get("/ui")
async def show_ui():
    file_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    return FileResponse(file_path)


@app.post("/generate-eye-mask")
async def generate_eye_mask(
    file: UploadFile = File(...), maskType: Optional[str] = Query(None)
):
    try:
        image_bytes = await file.read()
        mask_buffer = detect_and_mask_eyes(image_bytes, maskType)

        if mask_buffer == None:
            return {"isSuccess": False, "url": None}

        mask_url = upload_file(mask_buffer.getvalue(), f"mask_{file.filename}")

        return {"isSuccess": True, "url": mask_url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print("Error while generating mask", e)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6969)
