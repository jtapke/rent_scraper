import psycopg2
from datetime import datetime


class DatabaseOperations:

    def __init__(self):
        # Initialize database connection and cursor.
        self.connection = psycopg2.connect(
            dbname="locale",
            user="jordan",
            password="jordan",
            host="localhost"
        )
        self.cursor = self.connection.cursor()

    def get_latest_apartment(self, unit_id):
         # Fetch the latest entry for a unit to check for changes.
        query = """
            SELECT beds, baths, sqft, price, term_months, availability 
            FROM apartments 
            WHERE unit_id = %s 
            ORDER BY created_at DESC 
            LIMIT 1;
        """
        self.cursor.execute(query, (unit_id,))
        result = self.cursor.fetchone()
        return result  # Returns a tuple of the latest data (or None)

    def save_apartments(self, apartment):
        # Insert a new record only if data has changed.
        latest_data = self.get_latest_apartment(apartment["unit_id"])

        # If no existing data or data has changed, insert a new row
        if (not latest_data) or (self._has_changed(apartment, latest_data)):
            query = """
                INSERT INTO apartments 
                (unit_id, beds, baths, sqft, price, term_months, availability, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """
            self.cursor.execute(query, (
                apartment["unit_id"],
                apartment["beds"],
                apartment["baths"],
                apartment["sqft"],
                apartment["price"],
                apartment["term_months"],
                apartment["availability"],
                datetime.now()  # Explicit timestamp
            ))
            self.connection.commit()

    def _has_changed(self, new_data, latest_data):
        # Compare new data with the latest database entry.
        # Convert tuple to dict (order: beds, baths, sqft, price, term_months, availability)
        keys = ["beds", "baths", "sqft", "price", "term_months", "availability"]
        latest_dict = dict(zip(keys, latest_data))
        
        # Check if any field has changed
        return any(
            new_data[key] != latest_dict[key] 
            for key in keys
        )

    def close(self):
        """Close the database connection."""
        self.cursor.close()
        self.connection.close()