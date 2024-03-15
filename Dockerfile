# Use the official Python image as a base
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the Python script into the container
COPY . /app

# Execute the Python script
CMD ["python", "script.py"]
