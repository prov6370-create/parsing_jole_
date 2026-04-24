import asyncio
import aiohttp
import sqlite3
from aiohttp import ClientSession
from bs4 import BeautifulSoup
import re




def header():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'uk-UA,uk;q=0.9,ru;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    return headers

async def fetch(session, url, semaphore, raz=3):
    async with semaphore:
        for item in range(raz):
            try:
                async with session.get(url) as response:
                    response.raise_for_status()
                    return await response.text()
            except (ClientSession, aiohttp.ClientConnectorError) as e:
                print(f'ошыбка url {url} название ошибки {e} ')
            await asyncio.sleep(2)

async def parsing_url_catalog():
    headers = header()
    url_golovna_storinca = 'https://azi.ua/'
    async with aiohttp.ClientSession(headers=headers) as session:
        semaphore = asyncio.Semaphore(10)
        html = await fetch(session, url_golovna_storinca, semaphore)
        soup = BeautifulSoup(html, 'html.parser')
        storinka_catalogov = soup.find('ul', class_='relative')

        # Твой паттерн правильный, оставляем его
        pattern = re.compile(
            r'menu-item menu-item-type-taxonomy menu-item-object-product_cat menu-item-has-children menu-item-\d+')

        catalog = storinka_catalogov.find_all('li', class_=pattern, recursive=False)

        url_catalog = []

        for catalo in catalog:
            catalog_url = catalo.find('a', recursive=False)
            if catalog_url:
                url_catalog.append({'name':catalog_url.text.strip(), 'catalog_url':catalog_url['href']})

    return url_catalog


async def parsing_max_pag():
    url_catalog = await parsing_url_catalog()
    headers = header()
    async with aiohttp.ClientSession(headers=headers) as session:
        semaphore = asyncio.Semaphore(10)
        tasks = [fetch(session, item['catalog_url'], semaphore) for item in url_catalog]
        html_url_catalog = await asyncio.gather(*tasks)
        for html, item in zip(html_url_catalog, url_catalog):
            max_pag = 1
            name = item['name']
            soup = BeautifulSoup(html, 'html.parser')

            # 1. Ищем контейнер навигации аккуратно
            nav = soup.find('nav', class_='woocommerce-pagination')

            if nav:
                pag_links = nav.find_all(['a', 'span'], class_='page-numbers')

                pages = []
                for link in pag_links:
                    text = link.text.strip()
                    if text.isdigit():
                        pages.append(int(text))

                if pages:
                    max_pag = max(pages)

            item['max_pag'] = max_pag
    return url_catalog


async def parsing_result():
    url_catalog = await parsing_max_pag()
    headers = header()
    result_html_nema = []
    async with aiohttp.ClientSession(headers=headers) as session:
        semaphore = asyncio.Semaphore(10)
        tasks = []
        for item in url_catalog:
            max_p = item.get('max_pag', 1)
            for p in range(1, max_p + 1):
                url = f"{item['catalog_url']}?paged={p}"
                tasks.append(fetch(session, url, semaphore))
        html_url_catalog = await asyncio.gather(*tasks)
        result_html_nema = []
        html_index = 0

        for item in url_catalog:
            name = item.get('name')
            max_p = item.get('max_pag', 1)

            for p in range(1, max_p + 1):

                current_html = html_url_catalog[html_index]

                result_html_nema.append({
                    'name': name,
                    'quantity': p,
                    'html': current_html
                })

                html_index += 1

    return result_html_nema


async def parcing_nema_price():
    url_catalog = await parsing_result()
    all_products = []

    for item in url_catalog:
        soup = BeautifulSoup(item['html'], 'html.parser')

        products = soup.find_all('div', class_='info')

        for prod in products:
            try:

                name_el = prod.find('h3', class_='title')
                name = name_el.get_text(strip=True) if name_el else "Без названия"
                price_div = prod.find('div', class_='price')
                price = "0"
                if price_div:
                    # Берем текст из span (там где 440 грн)
                    price_span = price_div.find('span')
                    if price_span:
                        price = price_span.get_text(strip=True)
                    else:
                        price = price_div.get_text(strip=True)

                all_products.append({
                    'category': item['name'],
                    'title': name,
                    'price': price
                })

            except Exception:
                continue

    return all_products


async def database():
    result = await parcing_nema_price()
    conn = sqlite3.connect('cosmetics_store.db')
    cursor = conn.cursor()
    for row in result:
        category = row['category']
        price = row['price']
        title = row['title']
        table_name = f"cat_{re.sub(r'\W+', '_', category)}"
        cursor.execute(f"""CREATE TABLE IF NOT EXISTS "{category}" (
id INTEGER PRIMARY KEY AUTOINCREMENT,
title TEXT UNIQUE,
price REAL
)""")

        cursor.execute(f"""
                    INSERT OR IGNORE INTO "{category}" (title, price)
                    VALUES (?, ?)
                """, (title, price))

    conn.commit()
    conn.close()
    print("Данные успешно сохранены без дублей!")


async def main():
    catalog = await database()




if __name__ == '__main__':
    asyncio.run(main())
