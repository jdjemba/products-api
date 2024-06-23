# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make the init.sh script executable
RUN chmod +x init.sh

# Expose the port that the Flask app will run on
EXPOSE 8001

# Define environment variable
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run the init.sh script to set up the database and start the Flask app
CMD ["sh", "./init.sh"]
