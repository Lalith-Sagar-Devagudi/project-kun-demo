# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Ensure Python output is sent straight to the terminal (e.g. for logging)
ENV PYTHONUNBUFFERED=1

# Install system dependencies (e.g. gcc is often needed for compiling some packages)
RUN apt-get update && apt-get install -y build-essential poppler-utils && rm -rf /var/lib/apt/lists/*

# Install Poetry (our dependency manager)
RUN pip install poetry

# Set the working directory
WORKDIR /app

# Copy only the Poetry configuration files first to leverage Docker layer caching
# (Assuming your pyproject.toml and poetry.lock are in the backend/app folder)
COPY backend/pyproject.toml backend/poetry.lock* ./backend/app/
# Copy .env file /Users/lalithsagar/Desktop/MyProjects/KUN/project-kun-demo/.env
COPY .env /app

# Change directory to where the backend code and dependencies are defined
WORKDIR /app/backend/app

# Install dependencies and skip installing the current project package
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi

# Now copy the entire project into the container
COPY . /app

# Expose the port the app runs on
EXPOSE 8000

# Run the FastAPI application using Uvicorn.
# The app mounts the frontend static files, so it will serve both backend and frontend.
CMD ["poetry", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
