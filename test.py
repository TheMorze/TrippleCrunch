import sqlalchemy

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String

engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)

metadata = MetaData()

products_table = Table(
    "products",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(30)),
    Column("price", Integer),
)

metadata.create_all(engine)

# Добавляем тестовые данные
with engine.connect() as conn:
    conn.execute(products_table.insert(), [
        {"title": "Laptop", "price": 1000},
        {"title": "Phone", "price": 500},
        {"title": "Tablet", "price": 300},
    ])
    conn.commit()


from sqlalchemy import select

def get_products_sorted_by_price(engine, products_table, descending):
    with engine.connect() as conn:
        res = conn.execute(
            select(products_table).order_by("price")
        )
        print(res.all())

get_products_sorted_by_price(engine, products_table, descending=True)