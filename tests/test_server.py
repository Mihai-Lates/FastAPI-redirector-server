import requests


class TestServer:
    def test_run(self):
        pass


if __name__ == "__main__":
    response = requests.post("http://127.0.0.1:8000/form")
    print(response.json())
