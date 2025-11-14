import requests

URL = "http://localhost:8000/train/data/export"

def main():
    print(f"Fetching training data from {URL} ...")
    r = requests.get(URL, stream=True)
    if r.status_code != 200:
        print("❌ Failed to fetch data:", r.status_code, r.text)
        return

    with open("training_data.csv", "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    print("✅ Wrote training_data.csv")

if __name__ == "__main__":
    main()
