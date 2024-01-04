import logging
import os
import signal

import uvicorn

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse, JSONResponse

from constants import (
    GOOGLE_DEFAULT_PORT,
    GOOGLE_HOST,
    PASSCODE,
    URL_A,
    URL_B,
)

from utils import is_form_closed, read_counters, write_counters


app = FastAPI()

fastapi_logger = logging.getLogger("fastapi")
server_logger = logging.getLogger("server")
server_logger.setLevel(logging.INFO)


@app.get("/")
async def root():
    return {"message": "status 200 OK"}


@app.get("/form")
async def form():
    if is_form_closed(url=URL_A) and is_form_closed(url=URL_B):
        return {"message": "Ne pare rau, dar chestionarul nu mai accepta raspunsuri."}

    visit_count, visit_count_A, visit_count_B = read_counters()

    # If one form is closed, redirect to the other one
    if is_form_closed(url=URL_A):
        try:
            write_counters(total=visit_count + 1, a=visit_count_A, b=visit_count_B + 1)
            return RedirectResponse(url=URL_B)
        except HTTPException as e:
            server_logger.error(f"An error occurred: {e}")
            raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

    if is_form_closed(url=URL_B):
        try:
            write_counters(total=visit_count + 1, a=visit_count_A + 1, b=visit_count_B)
            return RedirectResponse(url=URL_A)
        except HTTPException as e:
            server_logger.error(f"An error occurred: {e}")
            raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

    # Alternating logic for redirection
    if visit_count % 2 == 0:
        try:
            write_counters(total=visit_count + 1, a=visit_count_A + 1, b=visit_count_B)
            return RedirectResponse(url=URL_A)
        except HTTPException as e:
            server_logger.error(f"An error occurred: {e}")
            raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

    else:
        try:
            write_counters(total=visit_count + 1, a=visit_count_A, b=visit_count_B + 1)
            return RedirectResponse(url=URL_B)
        except HTTPException as e:
            server_logger.error(f"An error occurred: {e}")
            raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


@app.get("/users-{password}")
async def get_users(password: str):
    if password == PASSCODE:
        visit_count, visit_count_A, visit_count_B = read_counters()
        return {
            "message": {
                "Accesari link": visit_count,
                "Accesari link 1 ET": visit_count_A,
                "Accesari link 2 CT": visit_count_B,
            }
        }
    else:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"message": "Not authorized: wrong password"},
        )


@app.post("/users-{password}/{total}-{a}-{b}")
async def get_users(password: str, total: str, a: str, b: str):
    if password == PASSCODE:
        if int(a) + int(b) == int(total):
            write_counters(total=total, a=a, b=b)
            visit_count, visit_count_A, visit_count_B = read_counters()
            return {
                "message": {
                    "Accesari link": visit_count,
                    "Accesari link 1 ET": visit_count_A,
                    "Accesari link 2 CT": visit_count_B,
                }
            }
        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": "Incorrect data values."},
            )
    else:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"message": "Not authorized: wrong password"},
        )


@app.post("/shutdown-{password}")
async def server_stop(password: str):
    if password == PASSCODE:
        server_logger.info("Server shutting down...")
        os.kill(os.getpid(), signal.SIGTERM)
        return {"message": "Server shutting down..."}
    else:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"message": "Not authorized: wrong password"},
        )


def server_start():
    server_logger.info("Server starting...")
    uvicorn.run(
        app=app, host=GOOGLE_HOST, port=int(os.environ.get("PORT", GOOGLE_DEFAULT_PORT))
    )


if __name__ == "__main__":
    server_start()
