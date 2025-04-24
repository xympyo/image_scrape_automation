import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

BASE_URL = "https://carolinasdiecast.com"
COLLECTION_URL = BASE_URL + "/collections/new-arrivals"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)


def download_image(url, folder):
    filename = sanitize_filename(os.path.basename(urlparse(url).path))
    path = os.path.join(folder, filename)

    # Avoid redownloading if already exists
    if os.path.exists(path):
        return

    try:
        r = requests.get(url, headers=HEADERS, stream=True, timeout=10)
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
        print(f"  ✅ Downloaded: {filename}")
    except Exception as e:
        print(f"  ❌ Failed to download {url}: {e}")


def get_product_links():
    print(f"🧭 Getting product links from collection page...")
    try:
        r = requests.get(COLLECTION_URL, headers=HEADERS, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        links = set()

        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/products/" in href:
                full_url = urljoin(BASE_URL, href.split("?")[0])
                links.add(full_url)

        print(f"🔗 Found {len(links)} product links")
        return list(links)

    except Exception as e:
        print(f"❌ Error while scraping collection: {e}")
        return []


def scrape_images_from_product(url):
    print(f"\n🌀 Processing: {url}")
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        slug = urlparse(url).path.strip("/").replace("products/", "")
        folder = sanitize_filename(slug)
        os.makedirs(folder, exist_ok=True)

        img_tags = soup.find_all("img")
        print(f"🔍 Found {len(img_tags)} image tags")

        for img in img_tags:
            src = img.get("src") or img.get("data-src")
            if not src:
                continue

            # Skip logos and known non-product assets
            if any(x in src.lower() for x in ["logo", "icon", "header", "svg"]):
                continue

            if src.startswith("//"):
                src = "https:" + src
            elif src.startswith("/"):
                src = urljoin(BASE_URL, src)

            download_image(src, folder)

    except Exception as e:
        print(f"❌ Error processing product page {url}: {e}")


def main():
    product_links = get_product_links()
    for link in product_links:
        scrape_images_from_product(link)


if __name__ == "__main__":
    main()
