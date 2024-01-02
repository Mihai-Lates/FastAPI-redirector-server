import requests


class TestServer:
    def test_run(self):
        pass


if __name__ == "__main__":
    response = requests.get("http://0.0.0.0:8080/")
    print(response)
