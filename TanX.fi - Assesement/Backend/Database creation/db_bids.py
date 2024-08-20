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
CREATE TABLE bids (
    commodity_id VARCHAR(100),
    bid_price_month VARCHAR(1000),
    rental_duration VARCHAR(100) NOT NULL,
    bid_id VARCHAR(1000), 
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
