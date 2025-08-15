FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libldap2-dev \
    libsasl2-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy files
COPY . /app

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose Odoo default port
EXPOSE 8069

# Start Odoo
CMD ["python", "odoo-bin", "--config=odoo.conf"]
