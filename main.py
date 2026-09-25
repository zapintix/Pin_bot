from contextlib import asynccontextmanager
from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pybotx import build_command_accepted_response

from bot import bot


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🤖 Bot starting...")

    await bot.startup()

    print("🤖 Bot started")

    try:
        yield
    finally:
        print("🛑 Bot stopping...")
        await bot.shutdown()


app = FastAPI(lifespan=lifespan)


@app.post("/command")
async def command_handler(request: Request):
    bot.async_execute_raw_bot_command(
        await request.json(),
        request_headers=request.headers,
    )

    return JSONResponse(
        build_command_accepted_response(),
        status_code=HTTPStatus.ACCEPTED,
    )


@app.get("/status")
async def status_handler(request: Request):
    status = await bot.raw_get_status(
        dict(request.query_params),
        request_headers=request.headers,
    )

    return JSONResponse(status)


@app.post("/notification/callback")
async def callback_handler(request: Request):
    await bot.set_raw_botx_method_result(
        await request.json(),
        verify_request=False,
    )

    return JSONResponse(
        build_command_accepted_response(),
        status_code=HTTPStatus.ACCEPTED,
    )