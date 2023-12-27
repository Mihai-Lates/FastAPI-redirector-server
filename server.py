import logging
import os
import signal

import uvicorn

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse, JSONResponse

from constants import URL_A, URL_B, passcode


app = FastAPI()

fastapi_logger = logging.getLogger("fastapi")
server_logger = logging.getLogger("server")
server_logger.setLevel(logging.INFO)

# Counters to keep track of visits
visit_count = 0
visit_count_A = 0
visit_count_B = 0


@app.get("/form")
async def form():
    global visit_count
    global visit_count_A
    global visit_count_B

    # Alternating logic for redirection
    if visit_count % 2 == 0:
        try:
            visit_count += 1
            visit_count_A += 1
            return RedirectResponse(url=URL_A)
        except HTTPException as e:
            server_logger.error(f"An error occurred: {e}")
    else:
        try:
            visit_count += 1
            visit_count_B += 1
            return RedirectResponse(url=URL_B)
        except HTTPException as e:
            server_logger.error(f"An error occurred: {e}")


@app.get("/users-{password}")
async def users(password):
    if password == passcode:
        return {
            "message": {
                "Accesari link": visit_count,
                "Accesari link A": visit_count_A,
                "Accesari link B": visit_count_B,
            }
        }
    else:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "Not authorized: wrong password"},
        )


@app.post("/shutdown-{password}")
async def server_stop(password):
    if password == passcode:
        server_logger.info("Server shutting down...")
        os.kill(os.getpid(), signal.SIGTERM)
        return {"message": "Server shutting down..."}
    else:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "Not authorized: wrong password"},
        )


def server_run():
    server_logger.info("Server starting...")
    uvicorn.run(app=app, host="127.0.0.1", port=8000)
