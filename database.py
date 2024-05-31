import sqlite3

conn = sqlite3.connect("locations.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY,
    name TEXT,
    address TEXT,
    latitude REAL,
    longitude REAL,
    notifications TEXT
)
""")

conn.commit()
conn.close()
def view_locations():
    conn = sqlite3.connect("locations.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, address, latitude, longitude, notifications FROM locations")
    locations = cursor.fetchall()
    
    if not locations:
        print("No locations found in the database.")
    else:
        print("Saved Locations:")
        for location in locations:
            location_id, name, address, latitude, longitude, notifications = location
            print(f"ID: {location_id}")
            print(f"Name: {name}")
            print(f"Address: {address}")
            print(f"Latitude: {latitude}")
            print(f"Longitude: {longitude}")
            print(f"Notifications: {notifications}")
            print("-" * 30)
    
    conn.close()


def clear_database():
    conn = sqlite3.connect("locations.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM locations")
    conn.commit()
    conn.close()
    print("Database cleared.")





