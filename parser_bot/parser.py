import httpx
from bs4 import BeautifulSoup


async def parse_books(url: str = "https://books.toscrape.com/") -> list[dict]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=10.0) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
        except httpx.HTTPError as e:
            print(f"Ошибка запроса: {e}")
            return []

    soup = BeautifulSoup(response.text, "lxml")
    books = []

    # Ищем все карточки товаров на странице
    for pod in soup.select("article.product_pod"):
        # Название (полное название хранится в атрибуте title тега <a>)
        title_tag = pod.select_one("h3 a")
        title = title_tag.attrs.get("title") if title_tag else "Нет названия"

        # Цена
        price_tag = pod.select_one(".price_color")
        price = price_tag.get_text(strip=True) if price_tag else "Нет цены"

        # Относительная ссылка на страницу книги
        relative_url = title_tag.attrs.get("href") if title_tag else ""
        # Базовый URL сайта + относительный путь
        book_url = f"https://books.toscrape.com/{relative_url.replace('../', '')}" if relative_url else url

        books.append({
            "title": title,
            "price": price,
            "url": book_url
        })

    return books