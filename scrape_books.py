import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin

base_url = "https://books.toscrape.com/catalogue/page-{}.html"
book_base_url = "https://books.toscrape.com/catalogue/"
page = 1
all_books = []

rating_dict = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

# دالة لتنضيف السعر من الرموز الغريبة
def clean_price(text):
    return float(text.replace("£", "").replace("Â", "").strip())

while True:
    url = base_url.format(page)
    response = requests.get(url)
    if response.status_code != 200:
        break
    soup = BeautifulSoup(response.text, "html.parser")
    books = soup.find_all("article", class_="product_pod")
    if not books:
        break

    print(f"جاري استخراج الصفحة {page}، عدد الكتب: {len(books)}")

    for book in books:
        # اللينك للكتاب (نستخدم urljoin عشان نحل مشكلة ../)
        book_url = urljoin(book_base_url, book.h3.a["href"])

        # ندخل صفحة الكتاب
        book_res = requests.get(book_url)
        book_res.encoding = "utf-8"  # حل مشكلة الترميز
        book_soup = BeautifulSoup(book_res.text, "html.parser")

        # العنوان
        name = book_soup.find("div", class_="product_main").h1.get_text(strip=True)

        # الأسعار + الضريبة
        price_excl = clean_price(book_soup.find("th", string="Price (excl. tax)").find_next("td").get_text())
        price_incl = clean_price(book_soup.find("th", string="Price (incl. tax)").find_next("td").get_text())
        tax = clean_price(book_soup.find("th", string="Tax").find_next("td").get_text())

        # التوافر + عدد النسخ
        availability_text = book_soup.find("th", string="Availability").find_next("td").get_text(strip=True)
        in_stock = 1 if "In stock" in availability_text else 0
        stock_count = int(''.join(filter(str.isdigit, availability_text))) if any(ch.isdigit() for ch in availability_text) else 0

        # التقييم
        rating_tag = book.find("p", class_="star-rating")
        rating_word = rating_tag["class"][1] if rating_tag else "Zero"
        rating = rating_dict.get(rating_word, 0)

        # عدد المراجعات
        reviews = int(book_soup.find("th", string="Number of reviews").find_next("td").get_text(strip=True))

        # UPC
        upc = book_soup.find("th", string="UPC").find_next("td").get_text(strip=True)

        # التصنيف (Category)
        breadcrumb = book_soup.find("ul", class_="breadcrumb").find_all("li")
        category = breadcrumb[2].a.get_text(strip=True) if len(breadcrumb) > 2 else "Unknown"

        # الوصف
        desc_tag = book_soup.find("div", id="product_description")
        description = desc_tag.find_next("p").get_text(strip=True) if desc_tag else ""

        # رابط الصورة
        image_rel = book_soup.find("div", class_="item active").img["src"]
        image_url = urljoin("https://books.toscrape.com/", image_rel)

        all_books.append({
            "upc": upc,
            "name": name,
            "category": category,
            "price_excl": price_excl,
            "price_incl": price_incl,
            "tax": tax,
            "rating": rating,
            "in_stock": in_stock,
            "stock_count": stock_count,
            "reviews": reviews,
            "description": description,
            "book_url": book_url,
            "image_url": image_url
        })
    page += 1

# حفظ البيانات
df = pd.DataFrame(all_books)
df.to_excel("books_full_with_images.xlsx", index=False)
print(f"{len(all_books)} books_full_with_images.xlsx")
