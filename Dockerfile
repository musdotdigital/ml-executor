# Use an official Python runtime as a parent image
FROM python:3.10-slim-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential libssl-dev libffi-dev python3-dev

# Install Nginx
RUN apt-get update && apt-get install -y nginx

# Install Trivy
RUN apt-get update && apt-get install -y wget apt-transport-https gnupg lsb-release
RUN wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | apt-key add -
RUN echo deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main | tee -a /etc/apt/sources.list.d/trivy.list
RUN apt-get update && apt-get install -y trivy

# Copy requirements.txt and install Python dependencies
COPY ./requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Remove default Nginx configuration files
RUN if [ -f /etc/nginx/conf.d/default.conf ]; then rm /etc/nginx/conf.d/default.conf; fi

# Copy nginx configuration file
COPY nginx.conf /etc/nginx/conf.d

# Expose port
EXPOSE 80

# Start Nginx and Gunicorn
CMD ["sh", "-c", "gunicorn run:app --bind unix:/tmp/gunicorn.sock --workers 3 --daemon && nginx -g 'daemon off;'"]
