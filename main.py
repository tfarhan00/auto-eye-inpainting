import uvicorn

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from modules.replicate.helpers import inpaint_image_replicate
from modules.supabase.helpers import upload_file
from modules.masking import detect_and_mask_eyes


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_home():
    return {"message": "server is running"}


@app.post("/inpaint")
async def inpaint_endpoint(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()

        mask_buffer = detect_and_mask_eyes(image_bytes)
        print("mask buffer", mask_buffer)

        image_url = upload_file(image_bytes, file.filename)
        mask_url = upload_file(mask_buffer.getvalue(), f"mask_{file.filename}")
        print("image_url", image_url)
        print("mask_url", mask_url)

        output = await inpaint_image_replicate(image_url, mask_url)
        print("replicate output", output)

        return {"url": output[0]}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6969)
