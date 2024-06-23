import pandas as pd
from app import db, Product, User, app


def convert_to_float(value: str):
    try:
        return float(value)
    except:
        return None

def insert_data():
    # Read the CSV file
    df = pd.read_csv('Amazon_Products.csv')
    
    # Iterate over the rows of the DataFrame and insert each row into the database
    for index, row in df.iterrows():
        product = Product(
            name=row['name'],
            category=row['main_category'],
            price=convert_to_float(row['actual_price'].replace('₹', '').replace(',', '')),
            discount_price=convert_to_float(row['discount_price'].replace('₹', '').replace(',', '')),
            rating=convert_to_float(row['ratings']),
        )
        db.session.add(product)
    
    db.session.commit()


def add_user():
    db.session.add(
        User(name="user_1", email="user_1@eemi.com")
    )
    db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        add_user()
        insert_data()
