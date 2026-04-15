
# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements (optional if you have a requirements.txt)
COPY requirements.txt requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose port
EXPOSE 5000

# Run the app
#CMD ["python", "app.py"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]

