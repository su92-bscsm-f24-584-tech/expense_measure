# Base Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements/requirement.txt requirement.txt
RUN pip install --no-cache-dir -r requirement.txt -i https://pypi.org/simple

# Copy project files
COPY . .

# Expose Flask port
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]
