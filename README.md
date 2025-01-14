# NOKO API Data Loader
This enterprise-grade data integration solution that leverages the robust API capabilities of Noko Time to extract mission-critical time tracking information and seamlessly migrate it into our PostgreSQL data warehouse. This cutting-edge Python-based utility is engineered to optimize data ingestion processes, ensuring both efficiency and data integrity throughout the ETL (Extract, Transform, Load) pipeline.

By utilizing the pandas library, a powerful data manipulation tool in the Python ecosystem, I'm able to perform transformations on the extracted dataset before loading it into our PostgreSQL instance.

This strategic implementation will significantly enhance our organization's ability to perform granular analysis on time entry data, facilitating data-driven decision-making processes across various departments. The scalable nature of our PostgreSQL database environment ensures that we can accommodate growing data volumes while maintaining optimal query performance.

Furthermore, this tool represents a key component in our broader digital transformation strategy, aligning with our commitment to leveraging cutting-edge technologies to streamline operations and drive business value. By automating the data integration process, we're not only improving operational efficiency but also reducing the risk of human error associated with manual data entry.

## Author
Salvatore P. Mancuso

## Table of Contents

1. [Requirements](#requirements)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Code Overview](#code-overview)
   - [API Key and Database Credentials](#api-key-and-database-credentials)
   - [API Data Pull Functions](#api-data-pull-functions)
   - [Database Functions](#database-functions)
5. [Contributions](#contributions)
6. [License](#license)

## Requirements

- Python 3.x
- `requests` library
- `pandas` library
- `psycopg2` library
- A PostgreSQL database

## Installation

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up the API key and database credentials in the `./keys` directory:
   - `nokoapi.key`: should contain the API key and base URL, separated by a comma
   - `databaseCreds.key`: should contain the database hostname, database name, username, password, and port, each separated by a comma

## Usage

1. Run the script:
   ```bash
   python main.py
   ```

2. The script will:
   - Fetch data from the NOKO API
   - Process the data and save it to a DataFrame
   - Export the processed data to a CSV file
   - Create a PostgreSQL table and insert the data

## Code Overview

### API Key and Database Credentials

The script begins by reading the API key and database credentials from local files within the `./keys` directory.
- **databaseCreds.key** This file is a basic CSV structure with the Host, Database, User Name, Password, Port. For example 192.168.0.4, prodDatabase, JohnDoe, PassWord1234, 5432
- **nokoapi.key** This is a single file containing the key and the base API url from NOKO.  The key looks like this LKu38-THIS-IS-NOT-A-REAL-KEY01mLU83sa. The base URL will look like this "https://YourInstitutionName.nokotime.com/api/entries.json"


- **API Key Reading:**
  ```python
  with open("./keys/nokoapi.key", "r") as fileOpenApiKey:
      apiInfo = csv.reader(fileOpenApiKey)
      for row in apiInfo:
          apiKey = row[0]
          baseUrl = row[1]
  ```

- **Database Credentials Reading:**
  ```python
  with open("./keys/databaseCreds.key", "r") as rawDatabaseCreds:
      databaseCreds = csv.reader(rawDatabaseCreds)
      for row in databaseCreds:
          db_host = row[0]
          db_database = row[1]
          db_userName = row[2]
          db_password = row[3]
          db_port = row[4]
  ```

### API Data Pull Functions

The API data pull section includes two main functions: `fetch_api_data` and `mainAPIpull`.

- **fetch_api_data(page: int) -> List[Dict]:**
  - Fetches data from the NOKO API for a specific page.
  - Prints a success or failure message based on the response status.

  ```python
  def fetch_api_data(page: int) -> List[Dict]:
      url = f"{baseUrl}?page={page}" if page > 0 else baseUrl
      response = requests.get(url, headers=HEADERS)
  
      if response.status_code == 200:
          print(f"Successfully fetched data from page {page}.")
          return response.json()
      else:
          print(f"Failed to fetch data from page {page}. Status code: {response.status_code}")
          return []
  ```

- **mainAPIpull():**
  - This function fetches all pages of data from the API.
  - It processes the data into a DataFrame and exports it as a CSV file.

  ```python
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
  
      df = pd.json_normalize(all_data)
      df.columns = df.columns.str.replace('entry.', '')
  
      columns_to_drop = [
          'project_id', 'time_from', 'time_to', 'user_id', 'url', 'billable', 
          'invoiced_at', 'invoice_id', 'description_text', 'import_id', 
          'description', 'money_status', 'billable_status', 'tags', 'project.id'
      ]
  
      df = df.drop(columns=columns_to_drop, errors='ignore')
      df.columns = [col.replace('project.name', 'project_name') for col in df.columns]
      df.to_csv('all_entries_deduped.csv', index=False)
      return df
  ```

### Database Functions

- **create_table():**
  - Connects to the PostgreSQL database and creates a table if it does not already exist.
  - The table schema is predefined in the `create_table_query`.

  ```python
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
  ```

- **check_and_insert_or_update(df):**
  - Checks if a record exists in the database. If it does, the function updates the record; otherwise, it inserts a new record.

  ```python
  def check_and_insert_or_update(df):
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
  
          cur.execute(sql.SQL("SELECT 1 FROM {} WHERE id = %s").format(sql.Identifier('noko_time')), [record_id])
          exists = cur.fetchone()
  
          if exists:
              cur.execute(sql.SQL("SELECT recently_updated_at FROM {} WHERE id = %s").format(sql.Identifier('noko_time')), [record_id])
              recently_updated_at_DB = cur.fetchone()[0]
              if recently_updated_at_DB != recently_updated_at:
                  print(f"Record ID: {record_id} found and Updated")
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
  ```

## Contributions

Contributions to enhance this project are welcome. Feel free to create a pull request or open an issue for any bugs or feature requests.

## License

This project is open-source and available under the MIT License.
```