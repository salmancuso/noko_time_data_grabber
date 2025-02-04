import psycopg2
from psycopg2 import sql
import regex as re
from config import db_host, db_database, db_userName, db_password

def create_table():
    try:
        conn = psycopg2.connect(
            host=db_host, database=db_database, user=db_userName, password=db_password
        )
        cur = conn.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS noko_time (
            id BIGINT PRIMARY KEY,
            date DATE,
            hours decimal,
            created_at TEXT,
            updated_at TEXT,
            formatted_description TEXT,
            recently_updated_at TEXT,
            user_name TEXT,
            project_name TEXT,
            tags TEXT
        )
        """
        cur.execute(create_table_query)
        conn.commit()
        conn.close()
    except (Exception, psycopg2.Error) as error:
        print("Error creating table:", error)

def check_and_insert_or_update(df):
    rawIDs = []
    conn = psycopg2.connect(
        host=db_host, database=db_database, user=db_userName, password=db_password
    )
    cur = conn.cursor()
    for index, row in df.iterrows():
        record_id = row['id']
        hours = float(float(row['minutes'])/60)
        rawIDs.append(record_id)
        recently_updated_at = row['recently_updated_at']
        tagsRaw = str(row['formatted_description'])
        pattern = r'#[a-zA-Z0-9-]+'
        matches = re.findall(pattern, tagsRaw)

        tags = matches[0] if matches else str()

        cur.execute(sql.SQL("SELECT 1 FROM {} WHERE id = %s").format(sql.Identifier('noko_time')), [record_id])
        exists = cur.fetchone()

        if exists:
            cur.execute(sql.SQL("SELECT recently_updated_at FROM {} WHERE id = %s").format(sql.Identifier('noko_time')), [record_id])
            recently_updated_at_DB = cur.fetchone()[0]
            if recently_updated_at_DB != recently_updated_at:
                update_query = sql.SQL("""
                    UPDATE {} SET
                    date = %s, hours = %s, created_at = %s, updated_at = %s,
                    formatted_description = %s, recently_updated_at = %s,
                    user_name = %s, project_name = %s, tags = %s
                    WHERE id = %s
                """).format(sql.Identifier('noko_time'))
                cur.execute(update_query, (
                    row['date'], hours, row['created_at'], row['updated_at'],
                    row['formatted_description'], row['recently_updated_at'],
                    row['user_name'], row['project_name'], tags, row['id']
                ))
        else:
            insert_query = sql.SQL("""
                INSERT INTO {} (id, date, hours, created_at, updated_at, formatted_description, recently_updated_at, user_name, project_name, tags) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """).format(sql.Identifier('noko_time'))
            cur.execute(insert_query, (
                row['id'], row['date'], hours, row['created_at'], row['updated_at'],
                row['formatted_description'], row['recently_updated_at'],
                row['user_name'], row['project_name'], tags
            ))
        conn.commit()
    conn.close()
    delete_extra_ids(rawIDs)

def delete_extra_ids(rawIDs):
    conn = psycopg2.connect(
        host=db_host, database=db_database, user=db_userName, password=db_password
    )
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM noko_time")
        db_ids = [row[0] for row in cursor.fetchall()]

        ids_to_delete = set(db_ids) - set(rawIDs)

        if ids_to_delete:
            delete_query = "DELETE FROM noko_time WHERE id = ANY(%s)"
            cursor.execute(delete_query, (list(ids_to_delete),))
            conn.commit()
        else:
            print("No extra IDs found in the database.")

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL or executing query:", error)

    finally:
        if conn:
            cursor.close()
            conn.close()