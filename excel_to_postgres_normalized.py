import pandas as pd
from sqlalchemy import create_engine, inspect

# إعداد الاتصال بقاعدة البيانات

engine = create_engine("postgresql+psycopg2://deeyab:808080@localhost:5433/booksdb")


inspector =  inspect(engine)
print("Tables in public schema:", inspector.get_table_names(schema="public"))

# قراءة ملف Excel

df = pd.read_excel("/Data/Downloads/Booklytics_Project/books_full_with_images.xlsx")

# تنظيف البيانات

df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

# التعامل مع التصنيفات

cat_df = pd.DataFrame(df['category'].unique(), columns=['name'])

# قراءة التصنيفات الموجودة بالفعل لتجنب التكرار
existing_cats = pd.read_sql("SELECT name FROM categories", engine)
new_cats = cat_df[~cat_df['name'].isin(existing_cats['name'])]

# إدخال التصنيفات الجديدة فقط
if not new_cats.empty:
    new_cats.to_sql("categories", engine,schema="public", if_exists="append", index=False)

# لكل كاتجوري ع الموقع ليها id
categories_db = pd.read_sql("SELECT id, name AS category_name FROM categories", engine)
df = df.merge(categories_db, how='left', left_on='category', right_on='category_name')
df.rename(columns={'id': 'category_id'}, inplace=True)


#بجهز بيانات الكتب
books_df = df[['upc','category_id', 'price_excl', 'tax', 'rating', 'in_stock', 
               'stock_count', 'reviews', 'name', 'description', 'book_url', 'image_url']].copy()

# علي الموقع ف هنا بحولها بتروو \ وفولسin_stockف
books_df['in_stock'] = books_df['in_stock'].astype(bool)
# بدخل الكتب من هنا
books_df.to_sql("books", engine, schema="public", if_exists="append", index=False)
print("Data entered successfully")
