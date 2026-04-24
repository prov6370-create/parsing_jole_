# 💄 Asynchronous Cosmetics Scraper | `azi.ua`

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Aiohttp](https://img.shields.io/badge/Aiohttp-Async--Request-FFD43B?style=for-the-badge&logo=python&logoColor=black)
![SQLite](https://img.shields.io/badge/SQLite3-Storage-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Status](https://img.shields.io/badge/Status-Production--Ready-success?style=for-the-badge)

**Високопродуктивний асинхронний інструмент** для повного витягування даних з маркетплейсу косметики. Побудований на базі неблокуючого вводу-виводу для досягнення максимальної швидкості.

---

### 🚀 Ключові фішки

* **⚡️ Turbo Async Engine**: Використання `asyncio` та `aiohttp` дозволяє парсити сотні товарів одночасно, що в рази швидше за звичайні синхронні скрипти.
* **🛡 Smart Load Control**: Вбудований семафор (`Semaphore`) обмежує кількість паралельних запитів, імітуючи органічне навантаження та запобігаючи бану.
* **📂 Dynamic DB Schema**: Скрипт на льоту аналізує категорії магазину та автоматично створює для кожної з них окрему таблицю в SQLite.
* **💎 Data Integrity**: Система `UNIQUE` ключів та стратегія `INSERT OR IGNORE` гарантують відсутність дублів у вашій базі.

---

### 📊 Об'єкти збору (Dataset)

Парсер витягує повний набір даних про кожен товар:
* ✅ **Назва** (Title) — повне найменування.
* ✅ **Ціна** (Price) — актуальна вартість у числовому форматі.
* ✅ **Категорія** (Category) — автоматичне групування.
* ✅ **Параметри** (Specs) — об'єм, країна-виробник, тип шкіри тощо.

---

### 🛠 Технологічний стек

| Компонент | Технологія | Роль у проекті |
| :--- | :--- | :--- |
| **Runtime** | `Python 3.10+` | Основа логіки та керування потоками |
| **Networking** | `aiohttp` | Блискавичні асинхронні HTTP-запити |
| **Parsing** | `BS4 (LXML)` | Високоточне витягування даних з DOM |
| **Database** | `SQLite3` | Надійне локальне сховище без зайвих залежностей |

---

### ⚙️ Встановлення та запуск

1. **Клонуй репозиторій:**
   ```bash
   git clone [https://github.com/your-username/azi-scraper.git](https://github.com/your-username/azi-scraper.git)
   cd azi-scraper
