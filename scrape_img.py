import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

BASE_URL = "https://carolinasdiecast.com"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)


def download_image(url, folder):
    filename = sanitize_filename(os.path.basename(urlparse(url).path))
    path = os.path.join(folder, filename)

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


def get_all_collections():
    print("🧭 Getting all collection links...")
    try:
        r = requests.get(BASE_URL + "/collections", headers=HEADERS)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        links = set()
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/collections/" in href and "/products/" not in href:
                full_url = urljoin(BASE_URL, href.split("?")[0])
                links.add(full_url)

        print(f"📚 Found {len(links)} collections")
        return list(links)

    except Exception as e:
        print(f"❌ Error while scraping collections: {e}")
        return []


def get_product_links_from_collection(collection_url):
    print(f"\n📂 Scraping collection: {collection_url}")
    try:
        r = requests.get(collection_url, headers=HEADERS)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        links = set()
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/products/" in href:
                full_url = urljoin(BASE_URL, href.split("?")[0])
                links.add(full_url)

        print(f"🔗 Found {len(links)} products in this collection")
        return list(links)

    except Exception as e:
        print(f"❌ Error scraping collection {collection_url}: {e}")
        return []


def scrape_images_from_product(url):
    images_root = "images"
    os.makedirs(images_root, exist_ok=True)

    folder = os.path.join(images_root, sanitize_filename(slug))
    os.makedirs(folder, exist_ok=True)

    print(f"\n🌀 Processing product: {url}")
    try:
        r = requests.get(url, headers=HEADERS)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        slug = urlparse(url).path.strip("/").replace("products/", "")
        folder = sanitize_filename(slug)
        os.makedirs(folder, exist_ok=True)

        img_tags = soup.find_all("img")
        print(f"🔍 Found {len(img_tags)} images")

        for img in img_tags:
            src = img.get("src") or img.get("data-src")
            if not src:
                continue

            # Skip logos and static assets
            if any(
                x in src.lower() for x in ["logo", "icon", "header", "svg", "avatar"]
            ):
                continue

            if src.startswith("//"):
                src = "https:" + src
            elif src.startswith("/"):
                src = urljoin(BASE_URL, src)

            download_image(src, folder)

    except Exception as e:
        print(f"❌ Error processing product page {url}: {e}")


def main():
    collection_links = get_all_collections()
    visited_products = set()

    for collection_url in collection_links:
        product_links = get_product_links_from_collection(collection_url)

        for product_url in product_links:
            if product_url in visited_products:
                continue
            visited_products.add(product_url)
            scrape_images_from_product(product_url)


if __name__ == "__main__":
    main()
