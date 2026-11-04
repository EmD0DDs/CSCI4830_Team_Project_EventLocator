from django.test import TestCase
import sqlite3




conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
cursor.execute("SELECT username FROM LoginSignup_user")
print(cursor.fetchall())
conn.close()


# Create your tests here.
