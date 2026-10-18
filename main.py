
import time
import uuid
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp, Scope, Receive, Send

EMAIL = "24f2006704@ds.study.iitm.ac.in"
ALLOWED_ORIGIN = "https://dash-y0oedo.example.com"

api = FastAPI()

api.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@api.get("/stats")
def get_stats(values: str = Query(...)):
    numbers = [int(x.strip()) for x in values.split(",")]

    if not numbers:
        return {"error": "At least one integer is required"}

    return {
        "email": EMAIL,
        "count": len(numbers),
        "sum": sum(numbers),
        "min": min(numbers),
        "max": max(numbers),
        "mean": sum(numbers) / len(numbers),
    }


class RequestHeadersMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send
    ):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = str(uuid.uuid4())
        start = time.perf_counter()

        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                elapsed = max(0.0, time.perf_counter() - start)
                headers = list(message.get("headers", []))
                headers.extend([
                    (b"x-request-id", request_id.encode()),
                    (b"x-process-time", f"{elapsed:.6f}".encode()),
                ])
                message["headers"] = headers

            await send(message)

        await self.app(scope, receive, send_with_headers)


app = RequestHeadersMiddleware(api)
