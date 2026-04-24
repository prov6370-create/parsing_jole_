import asyncio
import aiohttp
import sqlite3
from aiohttp import ClientError
from bs4 import BeautifulSoup
import re


# ---------------- HEADERS ----------------
def get_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'uk-UA,uk;q=0.9,ru;q=0.8,en;q=0.7',
    }


# ---------------- FETCH ----------------
async def fetch(session, url, semaphore, retries=3):
    async with semaphore:
        for _ in range(retries):
            try:
                async with session.get(url) as response:
                    response.raise_for_status()
                    return await response.text()

            except ClientError as e:
                print(f"[ERROR] {url}: {e}")
                await asyncio.sleep(2)

    return None


# ---------------- GET CATALOG ----------------
async def get_catalog():
    url = 'https://azi.ua/'

    async with aiohttp.ClientSession(headers=get_headers()) as session:
        semaphore = asyncio.Semaphore(10)

        html = await fetch(session, url, semaphore)
        soup = BeautifulSoup(html, 'html.parser')

        menu = soup.find('ul', class_='relative')
        pattern = re.compile(r'menu-item.*product_cat.*')

        catalog = []

        for li in menu.find_all('li', class_=pattern, recursive=False):
            a = li.find('a')
            if a:
                catalog.append({
                    'name': a.text.strip(),
                    'url': a['href']
                })

        return catalog


# ---------------- GET PAGES ----------------
async def get_pages(catalog):
    async with aiohttp.ClientSession(headers=get_headers()) as session:
        semaphore = asyncio.Semaphore(10)

        tasks = [fetch(session, item['url'], semaphore) for item in catalog]
        pages_html = await asyncio.gather(*tasks)

        for html, item in zip(pages_html, catalog):
            if not html:
                item['pages'] = 1
                continue

            soup = BeautifulSoup(html, 'html.parser')
            nav = soup.find('nav', class_='woocommerce-pagination')

            pages = [1]

            if nav:
                for p in nav.find_all(['a', 'span'], class_='page-numbers'):
                    if p.text.strip().isdigit():
                        pages.append(int(p.text.strip()))

            item['pages'] = max(pages)

        return catalog


# ---------------- COLLECT PRODUCTS ----------------
async def collect_products(catalog):
    async with aiohttp.ClientSession(headers=get_headers()) as session:
        semaphore = asyncio.Semaphore(10)

        tasks = []

        for cat in catalog:
            for page in range(1, cat['pages'] + 1):
                url = f"{cat['url']}?paged={page}"
                tasks.append((cat['name'], fetch(session, url, semaphore)))

        results = await asyncio.gather(*[t[1] for t in tasks])

        products = []
        idx = 0

        for cat in catalog:
            for _ in range(cat['pages']):
                html = results[idx]
                idx += 1

                if not html:
                    continue

                soup = BeautifulSoup(html, 'html.parser')
                items = soup.find_all('div', class_='info')

                for item in items:
                    title = item.find('h3', class_='title')
                    price = item.find('div', class_='price')

                    products.append({
                        'category': cat['name'],
                        'title': title.get_text(strip=True) if title else 'N/A',
                        'price': price.get_text(strip=True) if price else '0'
                    })

        return products


# ---------------- DATABASE ----------------
def save_to_db(products):
    conn = sqlite3.connect('cosmetics_store.db')
    cursor = conn.cursor()

    for p in products:
        safe_category = re.sub(r'\W+', '_', p['category'])

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS "{safe_category}" (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT UNIQUE,
                price TEXT
            )
        """)

        cursor.execute(f"""
            INSERT OR IGNORE INTO "{safe_category}" (title, price)
            VALUES (?, ?)
        """, (p['title'], p['price']))

    conn.commit()
    conn.close()
    print("[OK] Data saved successfully")


# ---------------- MAIN ----------------
async def main():
    catalog = await get_catalog()
    catalog = await get_pages(catalog)
    products = await collect_products(catalog)
    save_to_db(products)


if __name__ == "__main__":
    asyncio.run(main())
