import requests

# url = 'http://127.0.0.1:8000/api/v1/upload-game-report/'
# file_path = 'test/data/civ6TestSaves/teamer.Civ6Save'
# with open(file_path, "rb") as f:
#     files = {"file": (f.name, f, "text/plain")}  # (filename, file_object, content_type)
#     response = requests.post(url, files=files)

# # Print the server's response
# print(response.json())

# 68a3ebf27d4b0613e1e432ec
url = 'http://127.0.0.1:8000/matches/get-match/'
response = requests.get(url, data={"match_id": "68a3ebf27d4b0613e1e432ec"})
print(response.json())

url = 'http://127.0.0.1:8000/matches/update-match/'
response = requests.put(url, data={"match_id": "68a3ebf27d4b0613e1e432ec", "confirmed": True})
print(response.json())

