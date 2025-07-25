#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Update the package list and install Nginx, Python3, and pip
sudo apt-get update -y
sudo apt-get install -y nginx python3-pip

# Install project dependencies
pip3 install -r requirements.txt

# Stop the default Nginx service
sudo systemctl stop nginx

# Create a new Nginx configuration file for the application
sudo tee /etc/nginx/sites-available/securityhub-reporter > /dev/null <<'EOF'
server {
    listen 80;
    server_name your_domain_or_ip; # Replace with your domain or EC2 public IP

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable the new configuration by creating a symbolic link
sudo ln -sf /etc/nginx/sites-available/securityhub-reporter /etc/nginx/sites-enabled/

# Remove the default Nginx configuration
sudo rm -f /etc/nginx/sites-enabled/default

# Test the Nginx configuration for syntax errors
sudo nginx -t

# Start the Nginx service
sudo systemctl start nginx

# Start the Gunicorn server to run the Python application
# Replace 'app:app' with 'your_main_file:your_app_instance' if different
gunicorn --workers 3 --bind 127.0.0.1:8000 app:app --daemon

echo "Deployment successful!"