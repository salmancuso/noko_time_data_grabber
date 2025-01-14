# NOKO API Data Grabber
This data integration solution that leverages the API capabilities of Noko Time to extract time tracking information and migrate it into a PostgreSQL database. This Python-based utility is engineered to optimize data ingestion processes, ensuring both efficiency and data integrity throughout the ETL (Extract, Transform, Load) pipeline.

By utilizing the pandas library, a data manipulation tool in the Python ecosystem, I'm able to perform transformations on the extracted dataset before loading it into our PostgreSQL instance.

This implementation will enhance our organization's ability to perform analysis on time entry data, facilitating data-driven decision-making processes across various departments. The scalable nature of our PostgreSQL database environment ensures that we can accommodate growing data volumes while maintaining optimal query performance.

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

- **mainAPIpull():**
  - This function fetches all pages of data from the API.
  - It processes the data into a DataFrame and exports it as a CSV file.

### Database Functions

- **create_table():**
  - Connects to the PostgreSQL database and creates a table if it does not already exist.
  - The table schema is predefined in the `create_table_query`.

- **check_and_insert_or_update(df):**
  - Checks if a record exists in the database. If it does, the function updates the record; otherwise, it inserts a new record.

## Contributions

Contributions to enhance this project are welcome. Feel free to create a pull request or open an issue for any bugs or feature requests.

## License

This project is open-source and available under the MIT License.