# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the blockchain code into the container
COPY blockchain.py .

# Install Flask
RUN pip install Flask

# Expose port 5000 to allow external connections
EXPOSE 5000

# Command to run the Flask app
CMD ["python", "blockchain.py"]