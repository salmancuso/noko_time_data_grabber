import requests
import pandas as pd
import time
from typing import List, Dict
import psycopg2
from psycopg2 import sql
from datetime import datetime
import csv

#### Database Cres
with open("./keys/databaseCreds.key", "r") as rawDatabaseCreds:
    databaseCreds = csv.reader(rawDatabaseCreds)
    for row in databaseCreds:
        db_host = row[0]
        db_database = row[1]
        db_userName = row[2]
        db_password = row[3]
        db_port = row[4]

conn = psycopg2.connect(
host=db_host,
database=db_database,
user=db_userName,
password=db_password
)
cur = conn.cursor()