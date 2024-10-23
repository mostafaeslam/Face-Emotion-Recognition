# Use official Python image from DockerHub
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the project files into the container
COPY . .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Install ffmpeg and other dependencies
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

# Expose the port on which the app will run
EXPOSE 5000

# Define the command to run the application
CMD ["python", "app/app.py"]
