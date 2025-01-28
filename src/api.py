import os
import logging
from fastapi import FastAPI, HTTPException, status
from fastapi.params import Depends
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from .params import QueryParams
from .tasks import run_extraction_task
from typing import Literal

# Environment variables
DATABASE_URL = os.getenv("DATABASE_URL")  # PostgreSQL connection string


# Database connection context manager
@contextmanager
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def get_db_cursor(commit=False):
    with get_db_connection() as connection:
        cursor = connection.cursor()

        try:
            yield cursor
            if commit:
                connection.commit()
        finally:
            cursor.close()


# Create FastAPI app
app = FastAPI(
    summary="An API that for property valuations in Durban in 2022.",
    description="This API returns data on the valuations of Full and Sectional title properties in Durban in 2022. The data returned is scraped from https://valuation2022.durban.gov.za/.", 
    version="0.1.0",
    title="2022 Durban Property Valuations API"
    )


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/get_properties/property_type/{property_type}")
async def get_data(property_type: Literal["FULL", "SECT"], params: QueryParams = Depends(QueryParams.get_query_params)):
    try:
        table_name = "full_properties"
        if property_type == "FULL":
            table_name = "full_properties"
        elif property_type == "SECT":
            table_name = "sectional_properties"

        # Create DB query and values
        query, values = params.create_query(table_name)

        # Log the DB query
        logging.info("Query: %s", str(query))

        with get_db_cursor() as cursor:
            # Execute the query with values
            cursor.execute(query, values)  
            properties = cursor.fetchall()

            if properties:
                return [dict(property) for property in properties]
            else:
                # If no records found, run extraction task and query again
                run_extraction_task(property_type, params)
        query = sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name))
        cursor.execute(query)

        properties = cursor.fetchall()
        return [dict(property) for property in properties]
    
    except psycopg2.Error as e:
        logging.error("An error occurred: %s", str(e))

        # Raise an HTTPException with a detailed error message
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An error occurred while processing your request: {str(e)}",
        ) from e
    
    except Exception as e:
        logging.error("Unexpected error: %s", str(e))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        ) from e

