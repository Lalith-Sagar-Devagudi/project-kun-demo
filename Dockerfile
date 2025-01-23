# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables to prevent Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install Poetry
RUN pip install poetry

# Set the working directory in the container
WORKDIR /app

# Copy only the pyproject.toml and poetry.lock files to the working directory
COPY pyproject.toml poetry.lock* /app/

# Install the project dependencies using Poetry
RUN poetry install --no-root

# Copy the entire frontend application into the container
COPY . /app

# Make port 8001 available to the world outside this container
EXPOSE 8000

# Run the application
CMD ["poetry", "run", "uvicorn", "frontend.app:app", "--host", "0.0.0.0", "--port", "8000"]
