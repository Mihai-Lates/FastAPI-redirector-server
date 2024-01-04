import csv

import requests

from google.cloud import storage, exceptions

from constants import BUCKET_NAME, STORAGE_FILE


def is_form_closed(url: str):
    try:
        response = requests.get(url=url)
    except requests.RequestException as e:
        raise requests.RequestException(f"An error occurred: {e}")

    if "/closedform" in response.url:
        return True
    return False


def read_counters():
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(STORAGE_FILE)
    try:
        with blob.open(mode="r", encoding="UTF8") as results_file:
            reader = list(csv.reader(results_file))
            return int(reader[1][0]), int(reader[1][1]), int(reader[1][2])
    except exceptions.GoogleCloudError as e:
        raise exceptions.GoogleCloudError(
            f"File {STORAGE_FILE} in bucket {BUCKET_NAME} could not be read: {e}"
        )
    except csv.Error as e:
        raise csv.Error(
            f"File {STORAGE_FILE} in bucket {BUCKET_NAME} could not be read: {e}"
        )


def write_counters(total: int | str, a: int | str, b: int | str):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(STORAGE_FILE)
    try:
        with blob.open(mode="w", encoding="UTF8", newline="\n") as results_file:
            writer = csv.writer(results_file)
            writer.writerow(
                [
                    "Accesari link",
                    "Accesari link 1 ET",
                    "Accesari link 2 CT",
                ]
            )
            writer.writerow([total, a, b])
    except exceptions.GoogleCloudError as e:
        raise exceptions.GoogleCloudError(
            f"File {STORAGE_FILE} in bucket {BUCKET_NAME} could not be written to: {e}"
        )
    except csv.Error as e:
        raise csv.Error(
            f"File {STORAGE_FILE} in bucket {BUCKET_NAME} could not be written to: {e}"
        )
