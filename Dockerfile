# Use official Python image from DockerHub
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app.py

# Copy the project files into the container
COPY . /app.py

# Install the required Python packages
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Expose the port on which the app will run
EXPOSE 5000

# Define the command to run the application
CMD ["python", "main.py"]
