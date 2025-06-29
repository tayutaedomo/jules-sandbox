# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install uv
RUN pip install uv

# Copy the requirements file into the container
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN uv pip install --system --no-cache -r requirements.txt

# Copy the rest of the application's code into the container
COPY . .

# Command to run the application (optional, can be overridden)
CMD ["python", "src/main.py"]
