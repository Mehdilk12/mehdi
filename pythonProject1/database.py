import sqlite3
import json


def init_db():
    """Initialize the database and create tables if they do not exist."""
    try:
        with sqlite3.connect('files.db') as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS processed_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    variable_type TEXT,
                    column_names TEXT,
                    digit_choice TEXT
                )
            ''')
            c.execute('''
                CREATE TABLE IF NOT EXISTS processed_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id INTEGER,
                    data TEXT,
                    FOREIGN KEY(file_id) REFERENCES processed_files(id)
                )
            ''')
            conn.commit()
    except sqlite3.Error as e:
        print("Error initializing database:", e)


def add_digit_choice_column():
    """Add digit_choice column to the processed_files table if it doesn't exist."""
    try:
        with sqlite3.connect('files.db') as conn:
            c = conn.cursor()
            # Add the column if it does not already exist
            c.execute("PRAGMA table_info(processed_files)")
            columns = [column[1] for column in c.fetchall()]
            if 'digit_choice' not in columns:
                c.execute("ALTER TABLE processed_files ADD COLUMN digit_choice TEXT")
            conn.commit()
    except sqlite3.Error as e:
        print("Error adding digit_choice column:", e)

# Call this function once during setup to ensure the column is added
add_digit_choice_column()

def check_if_processed(file_id):
    """Check if a file has already been processed by its ID."""
    try:
        with sqlite3.connect('files.db') as conn:
            c = conn.cursor()
            c.execute('SELECT id FROM processed_files WHERE id = ?', (file_id,))
            result = c.fetchone()
            return result[0] if result else None
    except sqlite3.Error as e:
        print("Error checking if file is processed:", e)
        return None

def add_to_processed(variable_type, column_names, digit_choice):
    """Add a file to the processed files table."""
    try:
        with sqlite3.connect('files.db') as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO processed_files (variable_type, column_names, digit_choice) 
                VALUES (?, ?, ?)
            ''', (variable_type, json.dumps(column_names), digit_choice))
            conn.commit()
            return c.lastrowid
    except sqlite3.IntegrityError:
        print("File already processed.")
        return None
    except sqlite3.Error as e:
        print("Error adding file to database:", e)
        return None


def store_processed_data(df, variable_type, digit_choice):
    """Store processed data along with digit choice in the database."""
    file_id = add_to_processed(variable_type, df.columns.tolist(), digit_choice)  # Ajout de digit_choice
    if file_id is None:
        return  # File already processed or error

    try:
        with sqlite3.connect('files.db') as conn:
            c = conn.cursor()
            # Add a loop to store each row of df in processed_data
            for _, row in df.iterrows():
                c.execute('''
                    INSERT INTO processed_data (file_id, data)
                    VALUES (?, ?)
                ''', (file_id, json.dumps(row.to_dict())))
            conn.commit()
    except sqlite3.Error as e:
        print("Error storing processed data:", e)



def get_processed_files():
    """Retrieve a list of processed files including their digit choice."""
    try:
        with sqlite3.connect('files.db') as conn:
            c = conn.cursor()
            # Ensure to select the digit_choice from the processed_files table
            c.execute('SELECT id, variable_type, column_names, digit_choice FROM processed_files')
            files = c.fetchall()
        print("Processed files:", files)
        return [{'id': f[0], 'variable_type': f[1], 'column_names': json.loads(f[2]), 'digit_choice': f[3]} for f in files]
    except sqlite3.Error as e:
        print("Error retrieving processed files:", e)
        return []
def get_processed_data(file_id):
    """Retrieve processed data for a specific file."""
    try:
        with sqlite3.connect('files.db') as conn:
            c = conn.cursor()
            c.execute('SELECT data FROM processed_data WHERE file_id = ?', (file_id,))
            data = c.fetchall()
        print("Data for file ID", file_id, ":", data)
        print([json.loads(row[0]) for row in data])
        return [json.loads(row[0]) for row in data]
    except sqlite3.Error as e:
        print("Error retrieving processed data for file:", e)
        return []
