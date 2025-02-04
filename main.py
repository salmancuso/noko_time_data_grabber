#!/usr/bin/python3

from api_functions import mainAPIpull
from db_functions import create_table, check_and_insert_or_update

if __name__ == "__main__":
    # Pull api data, transform and put into a dataframe and store it in memory. 
    df = mainAPIpull()

    # CREATE TABLE
    create_table()

    # LOAD DATA INTO DATABASE
    check_and_insert_or_update(df)