# NOKO API Data Grabber

This data integration solution leverages the API capabilities of Noko Time to extract time tracking information and migrate it into a PostgreSQL database. This Python-based utility is engineered to optimize data ingestion processes, ensuring both efficiency and data integrity throughout the ETL (Extract, Transform, Load) pipeline.

By utilizing the pandas library, a data manipulation tool in the Python ecosystem, we're able to perform transformations on the extracted dataset before loading it into our PostgreSQL instance.

This implementation will enhance our organization's ability to perform analysis on time entry data, facilitating data-driven decision-making processes across various departments. The scalable nature of our PostgreSQL database environment ensures that we can accommodate growing data volumes while maintaining optimal query performance.

## Author
Sal Mancuso 

## Table of Contents

1. [Requirements](#requirements)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Code Structure](#code-structure)
5. [Configuration](#configuration)
6. [Contributions](#contributions)
7. [License](#license)

## Requirements

- Python 3.x
- `requests` library
- `pandas` library
- `psycopg2` library
- `regex` library
- `os` library
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

Run the main script:
```bash
python main.py
```

The script will:
- Fetch data from the NOKO API
- Process the data and save it to a DataFrame
- Create or update the PostgreSQL table with the fetched data

## Code Structure

The project is now structured into multiple files for better organization:

1. `config.py`: Contains configuration loading for API and database credentials.
2. `api_functions.py`: Includes functions for fetching and processing API data.
3. `db_functions.py`: Contains functions for database operations.
4. `main.py`: The main script that orchestrates the entire process.

## Configuration

### API Key and Database Credentials

The script reads the API key and database credentials from local files within the `./keys` directory.

- **databaseCreds.key**: This file is a basic CSV structure with the Host, Database, User Name, Password, Port. 
  Example: `192.168.0.4,prodDatabase,JohnDoe,PassWord1234,5432`

- **nokoapi.key**: This file contains the key and the base API url from NOKO. 
  Example: `LKu38-THIS-IS-NOT-A-REAL-KEY01mLU83sa,https://YourInstitutionName.nokotime.com/api/entries.json`

These configurations are loaded in the `config.py` file and used throughout the application.

## Contributions

Contributions to enhance this project are welcome. Feel free to create a pull request or open an issue for any bugs or feature requests.

## License

This project is open-source and available under the MIT License.