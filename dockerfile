# Usepipenv", "run", "fastapige
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy the requirements.txt file into the container
COPY Pipfile Pipfile.lock /app/

# Upgrading pip
RUN python -m pip install --upgrade pip

# Install pipenv to generate requirements.txt
RUN pip install pipenv && pipenv install --dev --system --deploy

# Copy the rest of the application code
COPY . /app/

# Copy .env.example to .env (as per the instructions)
RUN cp .env.example .env

# Expose the port FastAPI app will run on
EXPOSE 8000

# Run the FastAPI app using the correct command
CMD ["python", "server.py"]
