import os
import sqlite3
import logging

from sqlite3 import Connection


# DB setup
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "database.db")


def get_db_connection() -> Connection:
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # To access columns by name
    return conn


def list_db_tables(dummy_param: str) -> dict:
    """Lists all tables in the SQLite database.

    Args:
        dummy_param (str): This parameter is not used by the function
                           but helps ensure schema generation. A non-empty string is expected.
    Returns:
        dict: A dictionary with keys 'success' (bool), 'message' (str),
              and 'tables' (list[str]) containing the table names if successful.
    """

    try:
        logging.info(f"List db tables called with `{dummy_param}` params.")
        conn = get_db_connection()
        cursor = conn.cursor()
        logging.info("Fetching all tables from db...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        logging.info(f"Found `{len(tables)}` tables.")
        return {
            "success": True,
            "message": "Tables listed successfully.",
            "tables": tables,
        }
    except sqlite3.Error as e:
        logging.error(f"Error listing tables. Sqlite Error: {e}")
        return {"success": False, "message": f"Error listing tables: {e}", "tables": []}
    except Exception as e:
        logging.error(f"An unexpected error occurred while listing tables. Error: {e}")
        return {
            "success": False,
            "message": f"An unexpected error occurred while listing tables: {e}",
            "tables": [],
        }


def get_table_schema(table_name: str) -> dict:
    """Gets the schema (column names and types) of a specific table."""

    logging.info(f"Get table schema called with `{table_name}` params.")
    conn = get_db_connection()
    cursor = conn.cursor()
    logging.info(f"Fetching `{table_name}` table schema...")
    cursor.execute(f"PRAGMA table_info('{table_name}');")  # Use PRAGMA for schema
    schema_info = cursor.fetchall()
    conn.close()
    if not schema_info:
        logging.error(f"Table `{table_name}` not found or no schema information.")
        raise ValueError(f"Table '{table_name}' not found or no schema information.")

    logging.info(f"Table `{table_name}` schema found successfully.")
    columns = [{"name": row["name"], "type": row["type"]} for row in schema_info]
    logging.info(f"Table `{table_name}` has `{len(columns)}` many columns.")
    return {"table_name": table_name, "columns": columns}


def query_db_table(table_name: str, columns: str, condition: str) -> list[dict]:
    """Queries a table with an optional condition.

    Args:
        table_name: The name of the table to query.
        columns: Comma-separated list of columns to retrieve (e.g., "id, name"). Defaults to "*".
        condition: Optional SQL WHERE clause condition (e.g., "id = 1" or "completed = 0").
    Returns:
        A list of dictionaries, where each dictionary represents a row.
    """

    logging.info(
        f"Query db table called with `{table_name, columns, condition}` params."
    )
    conn = get_db_connection()
    cursor = conn.cursor()
    query = f"SELECT {columns} FROM {table_name}"
    if condition:
        query += f" WHERE {condition}"
    query += ";"

    try:
        logging.info(f"Executing query `{query}` on table `{table_name}`")
        cursor.execute(query)
        results = [dict(row) for row in cursor.fetchall()]
        logging.info(
            f"Query `{query}` executed successfully on table `{table_name}`. Result Count `{len(results)}`."
        )
    except sqlite3.Error as e:
        conn.close()
        logging.error(
            f"Error querying table `{table_name}` for query `{query}`. Error: {e}"
        )
        raise ValueError(f"Error querying table '{table_name}': {e}")
    conn.close()
    return results


def insert_data(table_name: str, data: dict) -> dict:
    """Inserts a new row of data into the specified table.

    Args:
        table_name (str): The name of the table to insert data into.
        data (dict): A dictionary where keys are column names and values are the
                     corresponding values for the new row.

    Returns:
        dict: A dictionary with keys 'success' (bool) and 'message' (str).
              If successful, 'message' includes the ID of the newly inserted row.
    """

    logging.info(f"Insert data called with `{table_name, data}` params.")
    if not data:
        logging.warning("No data provided for insertion")
        return {"success": False, "message": "No data provided for insertion."}

    conn = get_db_connection()
    cursor = conn.cursor()

    columns = ", ".join(data.keys())
    placeholders = ", ".join(["?" for _ in data])
    values = tuple(data.values())

    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

    try:
        logging.info(f"Executing query `{query}` on table `{table_name}`")
        cursor.execute(query, values)
        conn.commit()
        last_row_id = cursor.lastrowid
        logging.info(
            f"Query `{query}` executed successfully on table `{table_name}`. Last row modified with id `{last_row_id}`."
        )
        return {
            "success": True,
            "message": f"Data inserted successfully. Row ID: {last_row_id}",
            "row_id": last_row_id,
        }
    except sqlite3.Error as e:
        conn.rollback()  # Roll back changes on error
        logging.error(
            f"Error inserting data into table `{table_name}` for query `{query}`. Error: {e}"
        )
        return {
            "success": False,
            "message": f"Error inserting data into table '{table_name}': {e}",
        }
    finally:
        conn.close()


def delete_data(table_name: str, condition: str) -> dict:
    """Deletes rows from a table based on a given SQL WHERE clause condition.

    Args:
        table_name (str): The name of the table to delete data from.
        condition (str): The SQL WHERE clause condition to specify which rows to delete.
                         This condition MUST NOT be empty to prevent accidental mass deletion.

    Returns:
        dict: A dictionary with keys 'success' (bool) and 'message' (str).
              If successful, 'message' includes the count of deleted rows.
    """

    logging.info(f"Delete data called with `{table_name, condition}` params.")
    if not condition or not condition.strip():
        logging.warning("Deletion condition cannot be empty.")
        return {
            "success": False,
            "message": "Deletion condition cannot be empty. This is a safety measure to prevent accidental deletion of all rows.",
        }

    conn = get_db_connection()
    cursor = conn.cursor()

    query = f"DELETE FROM {table_name} WHERE {condition}"

    try:
        logging.info(f"Executing query `{query}` on table `{table_name}`")
        cursor.execute(query)
        rows_deleted = cursor.rowcount
        conn.commit()
        logging.info(
            f"Query `{query}` executed successfully on table `{table_name}`. `{rows_deleted}` rows deleted."
        )
        return {
            "success": True,
            "message": f"{rows_deleted} row(s) deleted successfully from table '{table_name}'.",
            "rows_deleted": rows_deleted,
        }
    except sqlite3.Error as e:
        conn.rollback()
        logging.error(
            f"Error deleting data from table `{table_name}` for query `{query}`. Error: {e}"
        )
        return {
            "success": False,
            "message": f"Error deleting data from table '{table_name}': {e}",
        }
    finally:
        conn.close()
