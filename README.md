# 💄 Asynchronous Cosmetics Scraper (azi.ua)

Professional Python-based web scraping tool designed to extract product data from an online store and store it in a structured SQLite database. Built with a focus on speed, reliability, and data integrity.

## 🚀 Key Features
- **High-Speed Execution:** Leverages `asyncio` and `aiohttp` for concurrent page processing.
- **Request Throttling:** Implements `asyncio.Semaphore` to manage concurrency and prevent server-side blocking.
- **Dynamic Database Architecture:** Automatically generates separate SQLite tables for each product category found.
- **Data Deduplication:** Uses `UNIQUE` constraints and `INSERT OR IGNORE` logic to ensure a clean database without duplicates.
- **Smart Pagination:** Automatically detects the number of pages in each category and crawls them all.

## 🛠 Tech Stack
- **Language:** Python 3.10+
- **Libraries:** BeautifulSoup4, aiohttp, asyncio, SQLite3, re
- **Architecture:** Asynchronous, Multi-layered parsing

## ⚙️ Installation & Usage
1. Clone the repository:
   ```bash
   git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
