#!/usr/bin/env python3
"""
调试代理 - 查看传递的头部信息
"""
import os
import httpx
from fastapi import FastAPI, Request, Response
import uvicorn

app = FastAPI()

@app.api_route("/debug/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def debug_proxy(path: str, request: Request):
    """调试代理，显示所有请求信息"""
    headers_info = dict(request.headers)
    body = await request.body()

    print("=" * 50)
    print(f"请求路径: /{path}")
    print(f"请求方法: {request.method}")
    print("请求头部:")
    for key, value in headers_info.items():
        print(f"  {key}: {value}")
    print(f"请求体: {body}")
    print("=" * 50)

    # 转发到后端
    target_url = f"http://127.0.0.1:8080/api/{path}"
    headers = dict(request.headers)
    headers.pop("host", None)
    headers.pop("content-length", None)

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=body
        )
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9999, log_level="info")
