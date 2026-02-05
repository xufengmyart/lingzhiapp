#!/usr/bin/env python3
"""
修复后的代理服务 - 正确的路由顺序
"""
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

# ============================================
# API代理路由 - 优先级最高
# ============================================

@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def api_proxy(path: str, request: Request):
    try:
        target_url = f"http://127.0.0.1:8080/api/{path}"
        method = request.method

        # 只保留必要的头部
        headers = {
            "Content-Type": request.headers.get("content-type", "application/json"),
            "Accept": "application/json",
        }

        body = await request.body()

        async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
            response = await client.request(
                method=method,
                url=target_url,
                headers=headers,
                content=body
            )

            return Response(
                content=response.content,
                status_code=response.status_code,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization",
                }
            )
    except Exception as e:
        return Response(status_code=502, content=f"Backend error: {e}")

# ============================================
# 静态文件路由
# ============================================

@app.get("/")
async def root():
    index_file = os.path.join(public_dir, "index.html")
    if os.path.exists(index_file):
        with open(index_file, 'r', encoding='utf-8') as f:
            return Response(content=f.read(), media_type="text/html")
    return Response(status_code=404)

@app.get("/{path:path}")
async def static_files(path: str):
    # 跳过API路由
    if path.startswith("api/"):
        return Response(status_code=404)

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

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9002, log_level="info")
