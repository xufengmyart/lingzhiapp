#!/usr/bin/env python3
import os
import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 禁用ByteFaaS运行时代理
os.environ["_BYTEFAAS_RUNTIME_PORT"] = ""

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

public_dir = "/workspace/projects/public"

@app.get("/")
async def root():
    index_file = os.path.join(public_dir, "index.html")
    if os.path.exists(index_file):
        with open(index_file, 'r', encoding='utf-8') as f:
            return Response(content=f.read(), media_type="text/html")
    return Response(status_code=404)

@app.get("/{path:path}")
async def static_files(path: str):
    if not path or path == "/":
        file_location = os.path.join(public_dir, "index.html")
    else:
        file_location = os.path.join(public_dir, path)
    
    if os.path.exists(file_location) and os.path.isfile(file_location):
        if path.endswith('.html'):
            with open(file_location, 'r', encoding='utf-8') as f:
                return Response(content=f.read(), media_type="text/html")
        else:
            return FileResponse(file_location)
    
    index_location = os.path.join(public_dir, "index.html")
    if os.path.exists(index_location):
        with open(index_location, 'r', encoding='utf-8') as f:
            return Response(content=f.read(), media_type="text/html")
    
    return Response(status_code=404)

@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def api_proxy(path: str, request: Request):
    try:
        target_url = f"http://127.0.0.1:8080/api/{path}"
        method = request.method
        headers = dict(request.headers)
        headers.pop("host", None)
        headers.pop("content-length", None)
        body = await request.body()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=method,
                url=target_url,
                headers=headers,
                content=body
            )
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
    except Exception as e:
        return Response(status_code=502, content=f"Backend error: {e}")

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000, log_level="info")
