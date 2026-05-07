# Use the Python image as the base
FROM python:3.12-slim

# Prevent Python from writing bytecode files and run in unbuffered mode
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create app folder and set permissions
RUN mkdir /app && chmod -R 777 /app

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt first to leverage Docker cache
COPY requirements.txt ./

# Install dependencies. This layer will be cached unless requirements.txt changes
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the source code
COPY . .

# Set the entrypoint command
CMD ["python", "-m", "digitalai.release.integration.wrapper"]