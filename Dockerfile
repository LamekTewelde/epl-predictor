# Start from a small Linux system with Python 3.10 installed
FROM python:3.10-slim

# Work inside a folder called /app
WORKDIR /app

# Install packages first (explained below)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your project
COPY . .

# Build the database by downloading the data
RUN python load_data.py

# Start the server
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]