import csv
import os

#### Get the current working directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# API Key
with open(f"{current_dir}/keys/nokoapi.key", "r") as fileOpenApiKey:
    apiInfo = csv.reader(fileOpenApiKey)
    for row in apiInfo:
        apiKey = row[0]
        baseUrl = row[1]   

# Database Creds
with open(f"{current_dir}/keys/databaseCreds.key", "r") as rawDatabaseCreds:
    databaseCreds = csv.reader(rawDatabaseCreds)
    for row in databaseCreds:
        db_host = row[0]
        db_database = row[1]
        db_userName = row[2]
        db_password = row[3]
        db_port = int(row[4])
        db_table = row[5]

HEADERS = {
    'X-NokoToken': apiKey,
    'Content-Type': 'application/json'
}