import requests
import os
import hashlib
from urllib.parse import urlparse

def get_filename_from_url(url: str) -> str:
    """Extracts a filename from the URL or generates one."""
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    return filename if filename else "downloaded_image.jpg"

def get_file_hash(content: bytes) -> str:
    """Generates a SHA256 hash of the file content to detect duplicates."""
    return hashlib.sha256(content).hexdigest()

def fetch_image(url: str, download_dir: str, seen_hashes: set) -> None:
    """Fetch and save an image from a given URL with safety precautions."""
    try:
        # Fetch with timeout and headers
        headers = {"User-Agent": "UbuntuImageFetcher/1.0"}
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()

        # Check headers for content-type
        content_type = response.headers.get("Content-Type", "")
        if not content_type.startswith("image/"):
            print(f"✗ Skipped (not an image): {url}")
            return

        # Duplicate detection
        file_hash = get_file_hash(response.content)
        if file_hash in seen_hashes:
            print(f"✗ Skipped duplicate: {url}")
            return
        seen_hashes.add(file_hash)

        # Prepare filename and save
        filename = get_filename_from_url(url)
        filepath = os.path.join(download_dir, filename)

        # Prevent overwriting existing files
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(filepath):
            filename = f"{base}_{counter}{ext}"
            filepath = os.path.join(download_dir, filename)
            counter += 1

        with open(filepath, "wb") as f:
            f.write(response.content)

        print(f"✓ Successfully fetched: {filename}")
        print(f"✓ Image saved to {filepath}")

    except requests.exceptions.RequestException as e:
        print(f"✗ Connection error for {url}: {e}")
    except Exception as e:
        print(f"✗ Error fetching {url}: {e}")

def main():
    print("Welcome to the Ubuntu Image Fetcher")
    print("A tool for mindfully collecting images from the web\n")

    # Get multiple URLs from user
    urls = input("Please enter image URLs (comma separated): ").split(",")

    # Create directory if it doesn't exist
    download_dir = "Fetched_Images"
    os.makedirs(download_dir, exist_ok=True)

    # Keep track of downloaded file hashes to prevent duplicates
    seen_hashes = set()

    for url in [u.strip() for u in urls if u.strip()]:
        fetch_image(url, download_dir, seen_hashes)

    print("\nConnection strengthened. Community enriched.")

if __name__ == "__main__":
    main()
