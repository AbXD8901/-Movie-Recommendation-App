import pandas as pd
import pymysql

# Load the data from CSV
data = pd.read_csv('Movies.csv')

# Connect to the MySQL database
connection = pymysql.connect(
    host='localhost',  
    user='root',  
    password='Abdeshmukh08',  
    database='moviengine'  
)

cursor = connection.cursor()

# Prepare the SQL query to insert data into the movies table
for _, row in data.iterrows():
    sql = """
    INSERT INTO movies (movie, release_date, rating, genre, overview, crew, budget, revenue, country)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (
        row['movie'],
        row['release_date'],
        row['rating'],
        row['genre'],
        row['overview'],
        row['crew'],
        row['budget'],
        row['revenue'],
        row['country']
    ))

# Commit the transaction
connection.commit()

# Close the connection
cursor.close()
connection.close()

print("Data loaded successfully!")
