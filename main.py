from server import server_run

if __name__ == "__main__":
    server_logger.info("Server starting...")
    uvicorn.run(app=app, host=GOOGLE_HOST, port=int(os.environ.get("PORT", GOOGLE_DEFAULT_PORT)))
