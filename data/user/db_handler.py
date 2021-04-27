import sqlite3
from datetime import datetime

class UsersDataHandler:

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.cursor = self.conn.cursor()

        self.create_table()

    def create_table(self):
        '''
        Creates table if it does not already exist
        '''
        query = '''
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            name TEXT,
            warning_level INTEGER,
            prev_warning TIMESTAMP,
            prev_apology TIMESTAMP
        )
        '''
        with self.conn:
            self.cursor.execute(query)

        

    def get_user_details(self, author):
        '''
        Retrieves all available users data
        '''
        query = f"""
        SELECT * FROM users
        WHERE id = {author.id}
        """
        self.cursor.execute(query)
        details = self.cursor.fetchall()
        if details is not None:
            return details[0]
        
    def get_all_users(self):
        '''
        Retrieves all the user id's currently available
        '''
        query = f"""
        SELECT id FROM users
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_warning_level(self, author):
        '''
        Retrieves the warning level of a user
        '''
        id = author.id
        query = f"""
        SELECT warning_level FROM users
        WHERE id == {id}
        """

        self.cursor.execute(query)
        level = self.cursor.fetchone()
        if level is not None:
            return level[0]

        return None

    def get_prev_warning(self, author):
        '''
        Gets the time stamp of the last issued warning to a user
        '''
        id = author.id
        query = f"""
        SELECT prev_warning FROM users
        WHERE id == {id}
        """        

        self.cursor.execute(query)
        time = self.cursor.fetchone()
        if time is not None:
            return time[0]

        print(f'ID: {id} not found in users')
        return None


    def does_user_exist(self, author):
        '''
        Checks if user id exists in table
        '''
        id = author.id
        query = f"""
        SELECT EXISTS(
            SELECT 1 FROM users
            WHERE id == {id}
        )
        """
        self.cursor.execute(query)
        return bool(self.cursor.fetchone()[0])

    def increase_warning_level(self, author):
        '''
        Increases the warning level of a user
        '''
        id = author.id

        exists = self.does_user_exist(author)

        if exists:
            current_warning_level = self.get_warning_level(author)
            current_time = datetime.now()
            query = f"""
            UPDATE users SET 
            warning_level = {current_warning_level + 1},
            prev_warning = '{current_time}'
            WHERE id = {id}
            """

        else:
            query = f"""
            INSERT INTO users VALUES(
                {id},
                '{author.name}',
                {1},
                '{datetime.now()}',
                NULL
            )
            """
            print(query)
        with self.conn:
            self.cursor.execute(query)

    def reset_warning_level(self, author):
        '''
        Resets the warning level of a user
        '''
        if not self.does_user_exist(author):
            return False

        query = f"""
        UPDATE users SET
        warning_level = 0,
        prev_warning = NULL
        WHERE id = {author.id}
        """
        with self.conn:
            self.cursor.execute(query)
        return True


    def get_prev_apology(self, author):
        '''
        Gets the time stamp of previous apolgy made by a user
        '''
        if not self.does_user_exist(author):
            return False

        query = f"""
        SELECT prev_apology "[timestamp]" FROM users
        WHERE id = {author.id}
        """
        self.cursor.execute(query)
        time = self.cursor.fetchone()
        if time is not None:
            return time[0]

    
    def set_prev_apology(self, author):
        '''
        Sets the current time as previous apology when a user apologizes
        '''
        if not self.does_user_exist(author):
            return False

        query = f"""
        UPDATE users SET prev_apology = '{datetime.now()}'
        WHERE id = {author.id}
        """
        with self.conn:
            self.cursor.execute(query)
        return True

         
    def reset_apology(self, author):
        '''
        Resets the previous apology timestamp
        '''
        if not self.does_user_exist(author):
            return False

        query = f"""
        UPDATE users SET prev_apology = NULL
        WHERE id = {author.id}
        """
        with self.conn:
            self.cursor.execute(query)
        return True