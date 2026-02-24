from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

app = FastAPI()

def fib(n: int):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail
        },
    )

@app.get("/fib")
def fibonacci(n: int):
    try:
        if n < 0 or not isinstance(n, int):
            raise ValueError("n must be non-negative integer")
        return {
            "result": fib(n)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
