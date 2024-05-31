from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sqlite3
from geopy.distance import geodesic
from plyer import notification
import time
import geocoder
app = Flask(__name__)
CORS(app)



mapbox_access_token = 'pk.eyJ1IjoiYXNod2luNzA4NyIsImEiOiJjbG9rZDM1cXcyYWU5MnFuMHNmZjlhcjh1In0.hcAobJCiE_DxM-SV3pnfIw'

@app.route('/')
def index():
    return render_template('index.html',current_lat=current_lat, current_lon=current_lon,nearby_locations= get_nearby_locations(current_lat, current_lon))


def get_current_coordinates():
   g = geocoder.ip('me')
   return g.latlng

notification_cooldown = 10  #seconds
current_lat, current_lon = 0,0
save_loco_lat = None
save_loco_lon = None
# dic stores last noti time for each loco
last_notification_time = {}


@app.route('/save_location_html', methods=['GET', 'POST'])
def save_location_html():
    global save_loco_lat
    global save_loco_lon
    if request.method == 'POST':
        location_id = request.form.get('location_id')
        location_name = request.form.get('location_name')
        location_address = request.form.get('location_address')
        location_latitude = save_loco_lat
        location_longitude = save_loco_lon
        location_notifications = request.form.get('location_notifications')

        save_location(location_id, location_name, location_address, location_latitude, location_longitude, location_notifications)
        return "Location saved."

    return render_template('save_location.html',save_loco_lat=save_loco_lat,save_loco_lon=save_loco_lon)

def save_location(id, name, address, latitude, longitude, notifications):
    conn = sqlite3.connect("locations.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM locations WHERE id = ?", (id,))
    existing_location = cursor.fetchone()

    if existing_location:
        cursor.execute("UPDATE locations SET name=?, address=?, latitude=?, longitude=?, notifications=? WHERE id=?",
                       (name, address, latitude, longitude, notifications, id))
    else:
        cursor.execute("INSERT INTO locations (id, name, address, latitude, longitude, notifications) VALUES (?, ?, ?, ?, ?, ?)",
                       (id, name, address, latitude, longitude, notifications))

    conn.commit()
    conn.close()



def get_nearby_locations(current_lat, current_lon, max_distance=5.9):
    conn = sqlite3.connect("locations.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, notifications, latitude, longitude FROM locations")
    nearby_locations = []

    for row in cursor.fetchall():
        location_name, notifications, lat, lon = row
        distance = geodesic((current_lat, current_lon), (lat, lon)).kilometers
        if distance <= max_distance:
            nearby_locations.append((location_name, notifications))
    conn.close()
    return nearby_locations

def send_notifications(nearby_locations):
    current_time = time.time()
    for location_name, notifications in nearby_locations:
        if location_name not in last_notification_time or current_time - last_notification_time[location_name] >= notification_cooldown:
            notification_title = f"You are near {location_name}"
            notification_text = f"Notifications: {notifications}"
            notification.notify(
                title=notification_title,
                message=notification_text,
                app_name="Location-Based Notifications",
                timeout=10
            )
            last_notification_time[location_name] = current_time


@app.route('/view_locations')
def view_locations():
    conn = sqlite3.connect("locations.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, address, latitude, longitude, notifications FROM locations")
    locations = cursor.fetchall()

    return render_template('view_locations.html', locations=locations)


def clear_database():
    conn = sqlite3.connect("locations.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM locations")
    conn.commit()
    conn.close()
    print("Database cleared.")



@app.route('/clear_database_html', methods=['GET', 'POST'])
def clear_database_html():
    if request.method == 'POST':
        clear_database() 
        return "Database cleared."

    return render_template('clear_database.html') 

@app.route('/from_MAP', methods=['GET', 'POST'])
def fromMap_location():
    if request.method == 'POST':

     data = request.get_json()
     latitude = data.get('latitude')
     longitude = data.get('longitude')

     return latitude, longitude
    return render_template('map.html')
  
 

@app.route('/done', methods=['GET'])
def done():
    if request.method == 'GET':
        return render_template('save_location.html')


@app.route('/get_live', methods=['POST'])
def get_live():
    global current_lat
    global current_lon
    if request.method == 'POST':
        try:
            data = request.get_json()  
            latitude = data['latitude']
            longitude = data['longitude']
            current_lat = latitude
            current_lon = longitude
            return "Location data received and processed successfully", 200
        except Exception as e:
            return f"Error processing location data: {str(e)}", 400
    






@app.route('/send-coordinates', methods=['POST'])
def send_coordinates():
    if request.method == 'POST':
            data = request.get_json() 
            latitude = data['latitude']
            longitude = data['longitude']
            global save_loco_lat
            global save_loco_lon
            save_loco_lat = latitude
            save_loco_lon = longitude
            print(save_loco_lat,save_loco_lon)
            return render_template('save_location.html')
            
    else:
        return None,None



@app.route('/start_tracking', methods=['GET', 'POST'])
def start_tracking():
    current_lat, current_lon = get_current_coordinates()
    nearby_locations = get_nearby_locations(current_lat, current_lon)

    if request.method == 'POST':
        if nearby_locations:
            send_notifications(nearby_locations)
            return "Notifications sent."
        else:
            return "No nearby locations found."

    return render_template('index.html', current_lat=current_lat, current_lon=current_lon,nearby_locations=nearby_locations) 



if __name__ == "__main__":
   app.run(host="0.0.0.0", port=5000)
