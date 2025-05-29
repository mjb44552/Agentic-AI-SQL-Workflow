
# Use an official Python runtime as a parent image.
# We choose a 'slim' variant for smaller image size, which is good practice.
FROM python:3.9-slim

# Set the working directory inside the container.
# This is where your application code will live.
WORKDIR /app

# Copy the requirements.txt file first.
# This allows Docker to cache this layer. If your dependencies don't change,
# Docker won't re-run the 'pip install' step on subsequent builds, speeding them up.
COPY requirements.txt .

# Install Python dependencies.
# '--no-cache-dir' helps keep the image size down by not storing pip's cache.
RUN pip install --no-cache-dir -r requirements.txt

# Copy all your application code into the container.
# This copies everything from the directory where the Dockerfile is located into /app inside the container.
COPY . .

# Define the command to run your application when the container starts.
# This will execute your 'main.py' script using the python interpreter.
CMD ["python", "main.py"]