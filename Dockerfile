# 1. Use an official Python runtime as a parent image
#FROM python:3.10-slim

# 2. Set the working directory in the container
#WORKDIR /app

# 3. Copy the requirements file and install dependencies
#COPY requirements.txt .
#RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of your application code into the container
#COPY . .

# 5. Tell Docker what command to run when the container starts
#CMD ["python", "app.py"]


FROM python:3.10-slim

# Install system dependencies, including ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# DVC Pull Step (crucial for automation)
# We will add this later for the full CI/CD
# RUN dvc pull

COPY . .

CMD ["python", "app.py"]