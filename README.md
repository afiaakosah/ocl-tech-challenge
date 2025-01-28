# Durban Property Valuation API

- **API Endpoint**: `/get_properties/property_type/{property_type}` - Fetches property valuation data. The user must specificy the kind of title property (Sectional, "SECT" or Full, "FULL"). 
- **Scheduled Data Extraction**: Runs every `n` days (configurable via `.env`).
- **Error Handling & Alerts**: Email alerts are sent in case of extraction errors.
- **Database**: PostgreSQL used to store the property valuation data.

## Prerequisites

- Python 3.8+
- PostgreSQL installed (only for a non-Docker setup)
- Pipenv for dependency management

## Installation

### **Option 1: With Docker**

1. Ensure you have Docker and Docker Compose installed.
2. Before running Docker, if `requirements.txt` is missing, generate it:

   ```bash
   pipenv shell
   pipenv install
   pipenv requirements > requirements.txt
   ```

3. Build and run the Docker container:

   ```bash
   docker-compose up --build
   ```

4. The FastAPI app will be available at `http://127.0.0.1:8000`. You can access the properties data at `http://127.0.0.1:8000/get_properties/property_type/{property_type}`.

### **Option 2: Without Docker (Assuming PostgreSQL is Installed)**

If you prefer to run the app without Docker and already have PostgreSQL installed, follow these steps:

1. **Activate Pipenv shell**:
   Make sure you’re inside the project directory and activate the virtual environment:

   ```bash
   pipenv shell
   ```

2. **Install dependencies**:
   Install the required dependencies using **Pipenv**:

   ```bash
   pipenv install
   ```

3. **Create the `.env` file**:
   Copy the `.env.example` template to create your `.env` file:

   ```bash
   cp .env.example .env
   ```

   Edit the `.env` file to provide your configuration (database name, email credentials, etc.).

4. **Run the development server**:

   Start the FastAPI app using the command:

   ```bash
   fastapi dev api.py
   ```

   The FastAPI app will be available at `http://127.0.0.1:8000`.

## Configuration (`.env`)

The following environment variables should be defined in the `.env` file:

```
DB_NAME=properties
EXTRACTION_INTERVAL=1  # in days

# Email alert configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
EMAIL_PASSWORD=your_password
RECIPIENT_EMAIL=recipient_email@example.com
```

## Usage

- **API Endpoint**: You can access the properties data at `http://127.0.0.1:8000/get_properties/property_type/{property_type}`.
  
  Example requests:

  ```bash
  curl http://127.0.0.1:8000/get_properties/property_type/FULL
  ```

    ```bash
  curl http://127.0.0.1:8000/get_properties/property_type/SECT?address=14 TAMMANY AVENUE, CROFTDENE
  ```

   ```bash
  curl http://127.0.0.1:8000/get_properties/property_type/FULL?rate_number=05530000
  ```
