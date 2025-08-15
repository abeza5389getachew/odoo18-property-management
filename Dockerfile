FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git build-essential python3-dev libldap2-dev libsasl2-dev libpq-dev curl fontconfig libxrender1 libxext6 xfonts-75dpi xfonts-base \
    && curl -o /tmp/wkhtml.deb -SL https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_amd64.deb \
    && apt install -y /tmp/wkhtml.deb \
    && rm /tmp/wkhtml.deb \
    && rm -rf /var/lib/apt/lists/*

# Create odoo user
RUN useradd -m -d /var/lib/odoo -U -r -s /bin/bash odoo

# Set working directory
WORKDIR /odoo

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . .

# Change ownership
RUN chown -R odoo:odoo /odoo

USER odoo

# Expose Odoo port
EXPOSE 8069

# Run Odoo
CMD ["python3", "odoo-bin", "-c", "odoo.conf"]
