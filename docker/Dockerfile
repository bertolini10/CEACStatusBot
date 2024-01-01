# Use the official Ubuntu image as the base image
FROM ubuntu:20.04

# Set environment variables to suppress warnings during installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Update the package repository and install necessary packages
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    && apt-get clean

# Set the working directory in the container
WORKDIR /CEACStatusBot

# Copy the local application code to the container
COPY . /CEACStatusBot

# Install any Python dependencies using pip
RUN  pip install -r requirements.txt
#RUN pip install pyinstaller
#RUN pyinstaller --onefile test.py

# Specify the command to run your Python application
#CMD ["python", "test.py"]
WORKDIR /CEACStatusBot/