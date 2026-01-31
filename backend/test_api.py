import requests
import os

API_BASE = "http://127.0.0.1:8000/api/v1"

def test_upload():
    print("Testing upload...")
    file_path = os.path.join("storage", "ABC.mp4") # Using an existing file to re-upload as test
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    with open(file_path, "rb") as f:
        files = {"file": ("test_upload.mp4", f, "video/mp4")}
        response = requests.post(f"{API_BASE}/media/upload", files=files)
        
    if response.status_code == 200:
        print("Upload successful!")
        print(response.json())
    else:
        print(f"Upload failed: {response.status_code}")
        print(response.text)

def test_list():
    print("\nListing takes...")
    response = requests.get(f"{API_BASE}/media/")
    if response.status_code == 200:
        takes = response.json()
        print(f"Total takes: {len(takes)}")
        for t in takes:
            print(f"ID: {t['id']}, Name: {t['file_name']}")
    else:
        print(f"List failed: {response.status_code}")

if __name__ == "__main__":
    test_upload()
    test_list()
