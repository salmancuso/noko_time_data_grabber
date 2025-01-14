import requests
import pandas as pd
import time
from typing import List, Dict
import psycopg2
from psycopg2 import sql
from datetime import datetime
import csv

######################################
### Grab API Key and Database Creds.
######################################
##### API Key
with open("./keys/nokoapi.key", "r") as fileOpenApiKey:
    apiInfo = csv.reader(fileOpenApiKey)
    for row in apiInfo:
        apiKey = row[0]
        baseUrl = row[1]   

#### Database Cres
with open("./keys/databaseCreds.key", "r") as rawDatabaseCreds:
    databaseCreds = csv.reader(rawDatabaseCreds)
    for row in databaseCreds:
        db_host = row[0]
        db_database = row[1]
        db_userName = row[2]
        db_password = row[3]
        db_port = row[4]
######################################
######################################


######################################
### Other Universal Elements
######################################
HEADERS = {
    'X-NokoToken': apiKey,
    'Content-Type': 'application/json'
}
######################################
######################################


######################################
### FUNCTIONS FOR API PULL
######################################

##### Fetch data from the NOKO API for a specific page.
def fetch_api_data(page: int) -> List[Dict]:
    """
    Args:
        page (int): The page number to fetch.

    Returns:
        List[Dict]: A list of entry dictionaries.
    """
    url = f"{baseUrl}?page={page}" if page > 0 else baseUrl
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        print(f"Successfully fetched data from page {page}.")
        return response.json()
    else:
        print(f"Failed to fetch data from page {page}. Status code: {response.status_code}")
        return []

#### Main API pull function to fetch all data from the API, process it, and export to CSV.
def mainAPIpull():  
    all_data = []
    page = 1

    while True:
        entries = fetch_api_data(page)
        if not entries:
            break

        all_data.extend(entries)
        page += 1
        time.sleep(.125)  # Rate limiting

    #### FOR TEST ONLY  
    #### entries = fetch_api_data(page)
    #### all_data.extend(entries)

    #### Convert all data to DataFrame
    df = pd.json_normalize(all_data)

    #### Remove 'entry.' prefix from column names
    df.columns = df.columns.str.replace('entry.', '')

    #### List of columns to drop
    columns_to_drop = [
        'project_id',
        'time_from',
        'time_to',
        'user_id',
        'url',
        'billable',
        'invoiced_at',
        'invoice_id',
        'description_text',
        'import_id',
        'description',
        'money_status',
        'billable_status',
        'tags',
        'project.id'
    ]
    
    df = df.drop(columns=columns_to_drop, errors='ignore')
    df.columns = [col.replace('project.name', 'project_name') for col in df.columns]
    df.to_csv('all_entries_deduped.csv', index=False)
    return(df)
######################################
######################################


######################################
#### FUNCTIONS FOR DATABASE
######################################       
#### Create the table
def create_table():
    try:
        conn = psycopg2.connect(
            host=db_host,
            database=db_database,
            user=db_userName,
            password=db_password
        )
        cur = conn.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS noko_time (
            id BIGINT PRIMARY KEY,
            date DATE,
            minutes INTEGER,
            created_at TEXT,
            updated_at TEXT,
            formatted_description TEXT,
            recently_updated_at TEXT,
            import_id TEXT,
            user_name TEXT,
            project_name TEXT
        )
        """
        cur.execute(create_table_query)
        conn.commit()
        conn.close()
        print("Table created successfully")
    except (Exception, psycopg2.Error) as error:
        print("Error creating table:", error)

#### Function to check if a record exists and then insert or update
def check_and_insert_or_update(df):
    #### Open database connection
    conn = psycopg2.connect(
    host=db_host,
    database=db_database,
    user=db_userName,
    password=db_password
    )
    cur = conn.cursor()
    for index, row in df.iterrows():
        record_id = row['id']
        recently_updated_at = row['recently_updated_at']

        #### Check if the record exists
        cur.execute(sql.SQL("SELECT 1 FROM {} WHERE id = %s").format(sql.Identifier('noko_time')), [record_id])
        exists = cur.fetchone()

        if exists:
            #### Check if recently_updated_at is different
            cur.execute(sql.SQL("SELECT recently_updated_at FROM {} WHERE id = %s").format(sql.Identifier('noko_time')), [record_id])
            recently_updated_at_DB = cur.fetchone()[0]
            if recently_updated_at_DB != recently_updated_at:
                print(f"Record ID: {record_id} found and Updated")
                #### Update the record
                update_query = sql.SQL("""
                    UPDATE {} SET
                    date = %s,
                    minutes = %s,
                    created_at = %s,
                    updated_at = %s,
                    formatted_description = %s,
                    recently_updated_at = %s,
                    user_name = %s,
                    project_name = %s
                    WHERE id = %s
                """).format(sql.Identifier('noko_time'))
                cur.execute(update_query, (
                    row['date'],
                    row['minutes'],
                    row['created_at'],
                    row['updated_at'],
                    row['formatted_description'],
                    row['recently_updated_at'],
                    row['user_name'],
                    row['project_name'],
                    row['id']
                ))
        else:
            #### Insert the record
            insert_query = sql.SQL("""
                INSERT INTO {} (id, date, minutes, created_at, updated_at, formatted_description, recently_updated_at, user_name, project_name) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """).format(sql.Identifier('noko_time'))
            cur.execute(insert_query, (
                row['id'],
                row['date'],
                row['minutes'],
                row['created_at'],
                row['updated_at'],
                row['formatted_description'],
                row['recently_updated_at'],
                row['user_name'],
                row['project_name']
            ))
        conn.commit()
    conn.close()

######################################
######################################
##### MAIN LOOP ######################
######################################
######################################

if __name__ == "__main__":
    #### Pull api data, transform and put into a dataframe and store it in memory. 
    df = mainAPIpull()

    #### CREATE TABLE
    create_table()

    #### LOAD DATA INTO DATABASE
    check_and_insert_or_update(df)