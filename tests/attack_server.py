import requests


if __name__ == "__main__":
    for i in range(10000):
        response = requests.get(
            "https://fastapi-link-redirector-server.uc.r.appspot.com/"
        )
