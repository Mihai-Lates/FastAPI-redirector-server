import logging
import os
import signal

import requests
import uvicorn

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse, JSONResponse
from requests import RequestException

from constants import GOOGLE_DEFAULT_PORT, GOOGLE_HOST, PASSCODE, URL_A, URL_B


app = FastAPI()

fastapi_logger = logging.getLogger("fastapi")
server_logger = logging.getLogger("server")
server_logger.setLevel(logging.INFO)

# Counters to keep track of visits
visit_count = 0
visit_count_A = 0
visit_count_B = 0


@app.get("/")
async def root():
    return {"message": "status 200 OK"}


@app.get("/form")
async def form():
    global visit_count
    global visit_count_A
    global visit_count_B

    if is_form_closed(url=URL_A) and is_form_closed(url=URL_B):
        return {"message": "Ne pare rau, dar chestionarul nu mai accepta raspunsuri."}

    visit_count += 1

    # If one form is closed, redirect to the other one
    if is_form_closed(url=URL_A):
        try:
            visit_count_B += 1
            return RedirectResponse(url=URL_B)
        except HTTPException as e:
            server_logger.error(f"An error occurred: {e}")
            raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

    if is_form_closed(url=URL_B):
        try:
            visit_count_A += 1
            return RedirectResponse(url=URL_A)
        except HTTPException as e:
            server_logger.error(f"An error occurred: {e}")
            raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

    # Alternating logic for redirection
    if visit_count % 2 == 0:
        try:
            visit_count_A += 1
            return RedirectResponse(url=URL_A)
        except HTTPException as e:
            server_logger.error(f"An error occurred: {e}")
            raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

    else:
        try:
            visit_count_B += 1
            return RedirectResponse(url=URL_B)
        except HTTPException as e:
            server_logger.error(f"An error occurred: {e}")
            raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


@app.get("/users-{password}")
async def users(password):
    if password == PASSCODE:
        return {
            "message": {
                "Accesari link": visit_count,
                "Accesari link 1 ET": visit_count_A,
                "Accesari link 2 CT": visit_count_B,
            }
        }
    else:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "Not authorized: wrong password"},
        )


@app.post("/shutdown-{password}")
async def server_stop(password):
    if password == PASSCODE:
        server_logger.info("Server shutting down...")
        os.kill(os.getpid(), signal.SIGTERM)
        return {"message": "Server shutting down..."}
    else:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "Not authorized: wrong password"},
        )


def is_form_closed(url: str):
    try:
        response = requests.get(url=url)
    except RequestException as e:
        server_logger.error(f"An error occurred: {e}")
        raise RequestException(f"An error occurred: {e}")

    if "/closedform" in response.url:
        return True
    return False


if __name__ == "__main__":
    server_logger.info("Server starting...")
    uvicorn.run(app=app, host=GOOGLE_HOST, port=int(os.environ.get("PORT", GOOGLE_DEFAULT_PORT)))
