import os
import requests
import pandas as pd
from sqlalchemy import create_engine
from bs4 import BeautifulSoup
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import execute_values
from psycopg2 import sql

base_url = "https://valuation2022.durban.gov.za/FramePages/"
form_page_url = "SearchType.aspx"
form_action_url = "SearchType.aspx"
search_result_url = "SearchResult.aspx"

session = requests.session()


def extract_search_request_data(soup, property_type: str = "FULL"):
    post_data = {
        "__EVENTTARGET": "btnGo",
        "__EVENTARGUMENT": "",
    }
    input_fields = soup.findAll("input")

    for field in input_fields:
        post_data[field["name"]] = field["value"]

    select_name = soup.find("select")["name"]
    options = soup.findAll("option")

    # Make a dictionary of select options and remove the empty first option
    options = list(map(lambda option: option["value"], options))[1:3]

    title_property_option = 1

    if property_type == "FULL":
        title_property_option = 1
    elif property_type == "SECT":
        title_property_option = 2

    selected_option = title_property_option
    post_data[select_name] = selected_option
    post_data.pop("btnGo", None)

    return post_data


class QueryParams(BaseModel):
    volume_no: str = None
    rate_number: int = None
    street_no: int = None
    street_name: str = None
    suburb: str = None
    erf: int = None
    portion: int = None
    deeds_town: int = None


def create_query_url(user_params: QueryParams = None):

    # Check if any user parameter is provided
    use_user_params = any(
        [
            getattr(user_params, "volume_no", None),
            getattr(user_params, "rate_number", None),
            getattr(user_params, "street_no", None),
            getattr(user_params, "street_name", None),
            getattr(user_params, "suburb", None),
            getattr(user_params, "erf", None),
            getattr(user_params, "portion", None),
            getattr(user_params, "deeds_town", None),
        ]
    )

    if use_user_params:
        # Use user parameters for all values
        volume_no = user_params.volume_no or ""
        rate_number = user_params.rate_number or ""
        street_no = user_params.street_no or ""
        street_name = user_params.street_name or ""
        suburb = user_params.suburb or ""
        erf = user_params.erf or ""
        portion = user_params.portion or ""
        deeds_town = user_params.deeds_town or ""
    else:
        # Use environment variables for all values
        volume_no = os.getenv("VOLUME_NO", "")
        rate_number = os.getenv("RATE_NUMBER", "")
        street_no = os.getenv("STREET_NO", "")
        street_name = os.getenv("STREET_NAME", "")
        suburb = os.getenv("SUBURB", "")
        erf = os.getenv("ERF", "")
        portion = os.getenv("PORTION", "")
        deeds_town = os.getenv("DEEDS_TOWN", "")

    scheme_name = os.getenv("SCHEME_NAME", "")
    section_number = os.getenv("SECTION_NUMBER", "")

    # Create query string
    query = f"?Roll=1&VolumeNo={volume_no}&RateNumber={rate_number}&StreetNo={street_no}&StreetName={street_name}&Suburb={suburb}&ERF={erf}&Portion={portion}&DeedsTown={deeds_town}&SchemeName={scheme_name}&SectionNumber={section_number}&All=false"

    return query


def get_results(data, user_params: QueryParams = None):
    post_response = session.post(base_url + form_action_url, data=data, verify=False)

    # Check if a redirect happens
    if post_response.status_code == 302 or "Location" in post_response.headers:
        redirect_url = post_response.headers["Location"]

        search_response = session.get(redirect_url)
        results_html = search_response.text
        search_results_soup = BeautifulSoup(results_html, "html.parser")
    else:
        search_results_soup = BeautifulSoup(post_response.text, "html.parser")

    parameter_string = create_query_url(user_params)
    search_data_response = session.get(
        base_url + search_result_url + parameter_string, verify=False
    ).content

    search_data_soup = BeautifulSoup(search_data_response, "html.parser")
    results_table = search_data_soup.find("table")

    # Initialize a list to store each row's data
    data = []

    # Extract table headings
    headers = [header.text.strip() for header in results_table.find_all("th")]

    for row in results_table.find_all("tr"):
        columns = row.find_all("td")
        if columns:
            data.append({headers[i]: col.text.strip() for i, col in enumerate(columns)})

    return data


def clean_data(data):
    # Load data into a DataFrame
    df = pd.DataFrame(data)

    # Remove non-numeric "Rate Number" entries
    df = df[df["Rate Number"].str.isnumeric()]

    # Normalize column names (convert to lowercase, replace spaces with underscores)
    df.columns = df.columns.str.lower().str.replace(" ", "_", regex=True)

    # Convert "registered_extent" to numeric, handling commas and empty strings
    df["registered_extent"] = pd.to_numeric(
        df["registered_extent"].str.replace(",", ""), errors="coerce"
    )

    # Replace empty strings with NaN (which maps to NULL in PostgreSQL)
    df.replace({"": None}, inplace=True)

    return df


def store_data_to_db(dataframe, connection, table_name: str):
    # Prepare data tuple list for insertion
    tuples = [tuple(x) for x in dataframe.to_numpy()]

    # Comma-separated column names
    cols = ",".join(list(dataframe.columns))

    # SQL query to execute
    query = sql.SQL("INSERT INTO {} ({}) VALUES %s ON CONFLICT DO NOTHING").format(
        sql.Identifier(table_name),
        sql.SQL(cols)
    )

    # Execute the query
    cursor = connection.cursor()
    try:
        execute_values(cursor, query, tuples)
        connection.commit()
    except Exception as e:
        connection.rollback()
        print(f"An error occurred: {e}")
    finally:
        cursor.close()

    print("Data successfully inserted into database.")


def extract_data(property_type: str = "FULL", user_params: QueryParams = None):
    try:
        print("Extracting data...")
        # Set up database connection
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME", "property-valuations"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
        )

        
        table_name = "properties" 
        if property_type == "FULL":
            table_name = "full_properties"
        elif property_type == "SECT":
            table_name = "sectional_properties"

        # create a table if it doesn't exist
        cursor = conn.cursor()
        create_table_query = sql.SQL("""
        CREATE TABLE IF NOT EXISTS {} (
            rate_number VARCHAR(255),
            legal_description TEXT,
            address TEXT,
            first_owner TEXT,
            use_code TEXT,
            rating_category TEXT,
            market_value VARCHAR(255),
            registered_extent REAL
        );
        """).format(sql.Identifier(table_name))
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()

        # Get form page HTML
        html = session.get(base_url + form_page_url, verify=False).content
        # Prettify HTML output
        mainPageSoup = BeautifulSoup(html, "html.parser")

        search_form_data = extract_search_request_data(mainPageSoup, property_type)
        result_data = get_results(search_form_data, user_params)

        dataframe = clean_data(result_data)
        dataframe.head()

        store_data_to_db(dataframe, conn, table_name)
        conn.close()
        print("Data Extraction Complete.")
    except Exception as e:
        raise Exception(
            "Something went wrong while extracting the data:", str(e)
        ) from e
