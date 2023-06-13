## export BUILD_VERSION=1.0.3; docker buildx build --platform linux/amd64 -t hmpark/rembg-api:${BUILD_VERSION} . && docker push hmpark/rembg-api:${BUILD_VERSION}
## 

import base64
from fastapi import FastAPI, UploadFile, File
from starlette.requests import Request
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from traceback import print_exception
from rembg import remove
from PIL import Image
import numpy as np
import io

async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        print_exception(e)
        return Response("Internal server error", status_code=500)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update with the origin of your Next.js app
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)
app.middleware('http')(catch_exceptions_middleware)

@app.post("/remove-bg")
async def remove_background(file: UploadFile = File(...)):
    contents = await file.read()
    input_img = Image.open(io.BytesIO(contents))
    output_img = remove(input_img, alpha_matting=True)
    bbox = output_img.getbbox()
    output_img = output_img.crop(bbox)
    img_io = io.BytesIO()
    output_img.save(img_io, format='PNG')
    img_io.seek(0)
    # Convert the image to a base64 encoded string
    img_str = base64.b64encode(img_io.getvalue()).decode()    
    return Response(content=f"data:image/png;base64,{img_str}", media_type="image/png")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
