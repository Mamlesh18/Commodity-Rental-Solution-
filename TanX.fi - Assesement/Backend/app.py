from flask import Flask, request, jsonify, make_response, session
from flask_cors import CORS
import psycopg2
from psycopg2 import sql
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, jsonify
import requests
from dotenv import load_dotenv
from datetime import datetime

app = Flask(__name__)
CORS(app) 
app.config['SECRET_KEY'] = 'efa8f62542204fb7a09e081699481658'  # Replace with your own secret key

hostname = 'localhost'
database = 'Commodity'
username = 'postgres'
pwd = 'mamlesh'
port_id = 5432


def get_db_connection():
    conn = psycopg2.connect(
        host=hostname,
        dbname=database,
        user=username,
        password=pwd,
        port=port_id
    )
    return conn

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'Alert!': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except:
            return jsonify({'Message': 'Invalid token'}), 403
        return f(*args, **kwargs)
    return decorated

@app.route('/lender_signup', methods=['POST'])
def lender_signup():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        insert_script = sql.SQL('INSERT INTO lender_signup (username,password,email) VALUES (%s, %s, %s)')
        cur.execute(insert_script, (username,  password,email))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        print(f"Error during signup: {e}")
        return jsonify({"error": str(e)}), 500
    

@app.route('/renter_signup', methods=['POST'])
def renter_signup():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        insert_script = sql.SQL('INSERT INTO renter_signup (username,password,email) VALUES (%s, %s, %s)')
        cur.execute(insert_script, (username,  password,email))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        print(f"Error during signup: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/login_lender', methods=['POST'])
def login_lender():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(sql.SQL('SELECT * FROM lender_signup WHERE email = %s AND password = %s'), (email, password))
        user = cur.fetchone()

        if user:
            token = jwt.encode({
                'user': email,
                'exp': datetime.utcnow() + timedelta(minutes=30)
            }, app.config['SECRET_KEY'], algorithm="HS256")

            update_script = sql.SQL('UPDATE lender_signup SET tokens = %s WHERE email = %s')
            cur.execute(update_script, (token, email))

            conn.commit()
            cur.close()
            conn.close()

            return jsonify({'token': token}), 200
        else:
            cur.close()
            conn.close()
            return jsonify({"message": "Invalid email or password"}), 401

    except Exception as e:
        print(f"Error during login: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/login_renter', methods=['POST'])
def login_renter():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(sql.SQL('SELECT * FROM renter_signup WHERE email = %s AND password = %s'), (email, password))
        user = cur.fetchone()

        if user:
            token = jwt.encode({
                'user': email,
                'exp': datetime.utcnow() + timedelta(minutes=30)
            }, app.config['SECRET_KEY'], algorithm="HS256")

            update_script = sql.SQL('UPDATE renter_signup SET tokens = %s WHERE email = %s')
            cur.execute(update_script, (token, email))

            conn.commit()
            cur.close()
            conn.close()

            return jsonify({'token': token}), 200
        else:
            cur.close()
            conn.close()
            return jsonify({"message": "Invalid email or password"}), 401

    except Exception as e:
        print(f"Error during login: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/protected', methods=['GET'])
@token_required
def protected():
    return jsonify({'message': 'This is protected data'})


@app.route('/commodity/list', methods=['POST'])

def create_commodity():
    data = request.json
    item_name = data.get('item_name')
    item_description = data.get('item_description')
    quote_price_per_month = data.get('quote_price_per_month')
    item_category = data.get('item_category')

    if not item_name or not item_description or not quote_price_per_month or not item_category:
        return jsonify({"status": "error", "message": "All fields are required"}), 400
    
    allowed_categories = ['Electronics', 'Furniture', 'Vehicles', 'Tools', 'Books'] 
    if item_category not in allowed_categories:
        return jsonify({"status": "error", "message": "Invalid item category"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        insert_script = sql.SQL('''INSERT INTO commodities (item_name, item_description, quote_price_per_month, item_category, created_at)
                                   VALUES (%s, %s, %s, %s, %s) RETURNING commodity_id, created_at''')
        cur.execute(insert_script, (item_name, item_description, quote_price_per_month, item_category, datetime.utcnow()))

        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({
            "status": "success",
            "message": "Commodity listed successfully",
            "payload": {
                "commodity_id": result[0],
                "quote_price_per_month": quote_price_per_month,
                "created_at": result[1]
            }
        }), 201

    except Exception as e:
        print(f"Error during commodity creation: {e}")
        return jsonify({"status": "error", "message": "Commodity could not be listed", "payload": {}}), 500

@app.route('/commodity/list', methods=['GET'])

def get_commodities():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        query = sql.SQL('SELECT commodity_id, created_at, quote_price_per_month, item_category FROM commodities')
        cur.execute(query)

        results = cur.fetchall()
        commodities = [
            {
                "commodity_id": row[0],
                "created_at": row[1],
                "quote_price_per_month": row[2],
                "item_category": row[3]
            }
            for row in results
        ]

        cur.close()
        conn.close()

        return jsonify({
            "status": "success",
            "message": "Available commodities fetched successfully",
            "payload": commodities
        }), 200

    except Exception as e:
        print(f"Error during fetching commodities: {e}")
        return jsonify({"status": "error", "message": "Could not fetch commodities", "payload": {}}), 500


@app.route('/accept', methods=['POST'])
def accept_bid():
    try:
        data = request.json  # Get JSON data from React.js
        commodity_id = data.get('commodity_id')
        bid_id = data.get('bid_id')
        status = data.get('status')

        if not commodity_id or not bid_id or status not in ['accepted', 'rejected']:
            return jsonify({"status": "error", "message": "Invalid input provided", "payload": {}}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # Update the commodity's status in the commodities table
        query = sql.SQL('''
            UPDATE commodities
            SET status = %s
            WHERE commodity_id = %s
            AND EXISTS (
                SELECT 1 FROM bids WHERE bid_id = %s AND commodity_id = %s
            )
        ''')

        cur.execute(query, (status, commodity_id, bid_id, commodity_id))
        conn.commit()

        if cur.rowcount == 0:
            return jsonify({"status": "error", "message": "Commodity or bid not found", "payload": {}}), 404

        cur.close()
        conn.close()

        return jsonify({
            "status": "success",
            "message": f"Bid has been {status} successfully",
            "payload": {}
        }), 200

    except Exception as e:
        print(f"Error during accepting/rejecting bid: {e}")
        return jsonify({"status": "error", "message": "Could not process the bid", "payload": {}}), 500

@app.route('/commodity/bid', methods=['POST'])
def place_bid():
    data = request.json
    commodity_id = data.get('commodity_id')
    bid_price_month = data.get('bid_price_month')
    rental_duration = data.get('rental_duration')

    if not commodity_id or not bid_price_month or not rental_duration:
        return jsonify({"status": "error", "message": "All fields are required"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        insert_script = sql.SQL('''INSERT INTO bids (commodity_id, bid_price_month, rental_duration, created_at)
                                   VALUES (%s, %s, %s, %s) RETURNING bid_id, created_at''')
        cur.execute(insert_script, (commodity_id, bid_price_month, rental_duration, datetime.utcnow()))

        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({
            "status": "success",
            "message": "Bid created successfully",
            "payload": {
                "commodity_id": commodity_id,
                "created_at": result[1]
            }
        }), 201

    except Exception as e:
        print(f"Error during bid creation: {e}")
        return jsonify({"status": "error", "message": "Bid could not be placed", "payload": {}}), 500

@app.route('/common/<int:commodity_id>/bid', methods=['GET'])
def common(commodity_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        query = sql.SQL('''
            SELECT
                c.commodity_id,
                c.item_name,
                c.item_description,
                c.quote_price_per_month,
                c.item_category,
                b.bid_price_month,
                b.rental_duration
            FROM
                commodities c
            JOIN
                bids b
            ON
                c.commodity_id = b.commodity_id
            WHERE
                c.commodity_id = %s
        ''')

        cur.execute(query, (commodity_id,))
        result = cur.fetchone()

        if result:
            commodity = {
                "commodity_id": result[0],
                "item_name": result[1],
                "item_description": result[2],
                "quote_price_per_month": result[3],
                "item_category": result[4],
                "bid_price_month": result[5],
                "rental_duration": result[6]
            }

            response = {
                "status": "success",
                "message": "Commodity fetched successfully",
                "payload": commodity
            }
        else:
            response = {
                "status": "error",
                "message": f"No commodity found with id {commodity_id}",
                "payload": {}
            }

        cur.close()
        conn.close()

        return jsonify(response), 200

    except Exception as e:
        print(f"Error during fetching commodity: {e}")
        return jsonify({"status": "error", "message": "Could not fetch commodity", "payload": {}}), 500

@app.route('/commodities/user/<string:email>', methods=['GET'])
def get_commodities_by_email(email):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        query = sql.SQL('''
            SELECT commodity_id, item_name, item_description, quote_price_per_month, item_category, status
            FROM commodities
            WHERE email = %s
        ''')
        cur.execute(query, (email,))

        results = cur.fetchall()
        commodities = [
            {
                "commodity_id": row[0],
                "item_name": row[1],
                "item_description": row[2],
                "quote_price_per_month": row[3],
                "item_category": row[4],
                "status": row[5]
            }
            for row in results
        ]

        cur.close()
        conn.close()

        return jsonify({
            "status": "success",
            "message": f"Commodities fetched successfully for user {email}",
            "payload": commodities
        }), 200

    except Exception as e:
        print(f"Error during fetching commodities for user {email}: {e}")
        return jsonify({"status": "error", "message": "Could not fetch commodities", "payload": {}}), 500

if __name__ == '__main__':
    app.run(debug=True)
