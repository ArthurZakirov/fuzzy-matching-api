import requests
import os
import json

path_1 = "data/addresses.csv"
key1 = "country"

path_2 = "output/indices.csv"
key2 = "country_id"

url = "http://127.0.0.1:8000/merge-tables/"

path_1 = os.path.join(os.path.dirname(__file__), "data/addresses.csv")
path_2 = os.path.join(os.path.dirname(__file__), "data/indices.csv")
output_path = os.path.join(os.path.dirname(__file__), "output/merged.csv")


files = {"file1": open(path_1, "rb"), "file2": open(path_2, "rb")}
data = {
    "key1": key1,
    "key2": key2,
    "threshold": 0,
    "use_embeddings": "true",
}

response = requests.post(url, files=files, data=data)

if "text/csv" in response.headers.get("Content-Type", ""):
    # Save the CSV response to a file
    with open(output_path, "w") as csv_file:
        csv_file.write(response.text)

else:
    print("Response is not in CSV format")
