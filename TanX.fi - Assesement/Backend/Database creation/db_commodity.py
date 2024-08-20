import psycopg2

# Database connection details
conn = psycopg2.connect(
    dbname="Commodity", 
    user="postgres", 
    password="mamlesh", 
    host="localhost", 
    port="5432"
)

# Create a cursor object
cur = conn.cursor()

# SQL commands to create the tables
create_lender_table = """
CREATE TABLE commodities (
    item_name VARCHAR(100),
    item_description VARCHAR(1000),
    quote_price_per_month VARCHAR(100) NOT NULL,
    item_category VARCHAR(1000), 
    created_at VARCHAR(1000)
);
"""




# Execute the SQL commands
cur.execute(create_lender_table)

# Commit the changes
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()

print("Tables created successfully.")
