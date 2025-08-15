FROM python:3.10-slim

# Install system dependencies (no libssl1.1)
RUN apt-get update && apt-get install -y \
    git build-essential python3-dev libldap2-dev libsasl2-dev libpq-dev \
    curl fontconfig libxrender1 libxext6 xfonts-75dpi xfonts-base \
    wkhtmltopdf \
 && rm -rf /var/lib/apt/lists/*

# Copy custom addons
COPY ./custom_addons /mnt/extra-addons

# Install Python dependencies
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy Odoo config and entrypoint
COPY . /mnt/odoo

WORKDIR /mnt/odoo
CMD ["./start.sh"]
