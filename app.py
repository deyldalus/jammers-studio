95% of storage used … If you run out, you can't create, edit and upload files. Get 30 GB for ₱10 for 3 months ₱49.
app.py DATA.txt
from flask import Flask, request, jsonify, Response
from flask_mysqldb import MySQL
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required
)
from dicttoxml import dicttoxml
import datetime

app = Flask(__name__)

# Database Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Archaeology@123!'
app.config['MYSQL_DB'] = 'jammers_studio' 

app.config['JWT_SECRET_KEY'] = 'secretkey'

mysql = MySQL(app)
jwt = JWTManager(app)

@app.route('/')
def home():
    return jsonify({'message': 'Jammers Studio API is running'})

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if username == 'admin' and password == 'admin123':
            access_token = create_access_token(identity=username)
            return jsonify({'access_token': access_token}), 200

        return jsonify({'error': 'Invalid username or password'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint: POST /studio_bookings
@app.route('/studio_bookings', methods=['POST'])
@jwt_required()
def add_booking():
    try:
        data = request.get_json()
        
        band_name = data.get('band_name')
        genre = data.get('genre')
        band_leader = data.get('band_leader')
        members_count = data.get('members_count')
        room_number = data.get('room_number')
        booking_date = data.get('booking_date')
        session_hours = data.get('session_hours')

        if not all([band_name, genre, band_leader, members_count, room_number, booking_date, session_hours]):
            return jsonify({'error': 'All fields are required'}), 400

        cur = mysql.connection.cursor()
        query = """
        INSERT INTO studio_bookings(band_name, genre, band_leader, members_count, room_number, booking_date, session_hours)
        VALUES(%s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(query, (band_name, genre, band_leader, members_count, room_number, booking_date, session_hours))
        mysql.connection.commit()
        cur.close()

        return jsonify({'message': 'Booking added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint: GET /studio_bookings
@app.route('/studio_bookings', methods=['GET'])
def get_bookings():
    try:
        format_type = request.args.get('format', 'json')
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM studio_bookings")
        rows = cur.fetchall()
        cur.close()

        bookings = []
        for row in rows:
            bookings.append({
                'id': row[0],
                'band_name': row[1],
                'genre': row[2],
                'band_leader': row[3],
                'members_count': row[4],
                'room_number': row[5],
                'booking_date': row[6].strftime('%Y-%m-%d'),
                'session_hours': row[7]
            })

        if format_type == 'xml':
            xml = dicttoxml(bookings, custom_root='studio_bookings', attr_type=False)
            return Response(xml, mimetype='application/xml')

        return jsonify(bookings)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint: GET /studio_bookings/<id>
@app.route('/studio_bookings/<int:id>', methods=['GET'])
def get_booking(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM studio_bookings WHERE id=%s", (id,))
        row = cur.fetchone()
        cur.close()

        if row is None:
            return jsonify({'error': 'Booking not found'}), 404

        booking = {
            'id': row[0], 'band_name': row[1], 'genre': row[2], 
            'band_leader': row[3], 'members_count': row[4], 
            'room_number': row[5], 'booking_date': row[6].strftime('%Y-%m-%d'), 
            'session_hours': row[7]
        }
        return jsonify(booking)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint: GET /studio_bookings/search
@app.route('/studio_bookings/search', methods=['GET'])
def search_bookings():
    try:
        keyword = request.args.get('band_name')
        if not keyword:
            return jsonify({'error': 'Please provide band_name parameter'}), 400

        cur = mysql.connection.cursor()
        query = "SELECT * FROM studio_bookings WHERE band_name LIKE %s"
        cur.execute(query, ("%" + keyword + "%",))
        rows = cur.fetchall()
        cur.close()

        results = []
        for row in rows:
            results.append({
                'id': row[0], 'band_name': row[1], 'genre': row[2], 
                'band_leader': row[3], 'members_count': row[4], 
                'room_number': row[5], 'booking_date': row[6].strftime('%Y-%m-%d'), 
                'session_hours': row[7]
            })
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint: DELETE /studio_bookings/<id>
@app.route('/studio_bookings/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_booking(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM studio_bookings WHERE id=%s", (id,))
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Booking deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)