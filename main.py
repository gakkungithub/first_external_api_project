from fastapi import FastAPI, HTTPException, Request
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI()

'''
フィボナッチ行列のn項の値を取得する
第1項を求める場合、その値は入力値n=1とnと合致するので、その値をそのまま返す。
第n項(i>=2)については、第2項, 第3項,...第n項と順に求めて
いけば求まるので、n-1回その計算を繰り返したら求まる(その結果、bにその値が格納される)
'''
def fib(n: int):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b

'''
HTTPExceptionをそのまま出すと、レスポンスのjsonのキーが
detail(エラーの詳細)だけになってしまうのでエラーメッセージをカスタマイズする
'''
@app.exception_handler(HTTPException)
async def value_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": str(exc.status_code),
            "message": exc.detail
        },
    )

'''fibエンドポイント以外にアクセスした場合(404エラー)にもカスタマイズしてレスポンスを返す'''
@app.exception_handler(StarletteHTTPException)
async def not_found_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": str(exc.status_code),
            "message": exc.detail
        },
    )

'''fibにアクセスしたがクエリにnが含まれない時もエラーを表示する'''
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "status": "422",
            "message": str(exc)
        },
    )

'''他のExceptionについてもカスタマイズしたメッセージを返す'''
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "status": "inner error",
            "message": str(exc)
        },
    )

'''
fibエンドポイントにアクセスされた時に実行される
入力した値が正の整数または20578(これを入力すると出力の桁数がpythonの限界である4300桁を超える)以上
ならその時点で「不正な値」を意味するエラーを出し、その内容をカスタマイズしてレスポンスとしてリクエスト側に返す
他のエラーについても同じ
エラーもなく正しい値を取得できたら、resultにその値を充てたstatus=200のjsonレスポンスを返す
'''
@app.get("/fib")
def fibonacci(n: int):
    try:
        if n <= 0:
            raise ValueError("n must be positive integer")
        elif n >= 20578:
            raise ValueError("n must be positive integer lower than 20578")
        return {
            "result": fib(n)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
