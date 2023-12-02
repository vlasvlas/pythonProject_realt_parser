import sqlite3


def connect():
    conn = sqlite3.connect('flats.db')
    return conn

a = 'some'

def create_flats_table():
    conn = connect()
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS flats(
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    flat_id TEXT unique,
    title TEXT,
    price INTEGER,
    description TEXT,
    image TEXT,
    rooms TEXT,
    square TEXT,
    year TEXT,
    floor TEXT,
    type_house TEXT,
    region TEXT,
    city TEXT,
    street TEXT,
    district TEXT,
    coordinates TEXT
    )""")


def insert_flat(flat: dict):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""INSERT INTO flats(flat_id,
    title, price,
    description,
    image ,
    rooms ,
    square ,
    year ,
    floor ,
    type_house ,
    region ,
    city ,
    street ,
    district ,
    coordinates 
    ) VALUES (:flat_id, 
    :title,
    :price,
    :description,
    :image ,
    :rooms ,
    :square ,
    :year ,
    :floor ,
    :type_house ,
    :region ,
    :city ,
    :street ,
    :district ,
    :coordinates)""", flat)

    conn.commit()
    conn.close()
