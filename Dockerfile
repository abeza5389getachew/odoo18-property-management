FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git build-essential python3-dev libldap2-dev libsasl2-dev libpq-dev \
    curl fontconfig libxrender1 libxext6 xfonts-75dpi xfonts-base \
 && rm -rf /var/lib/apt/lists/*

# Install wkhtmltopdf (static build)
RUN curl -o wkhtml.deb -L https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_amd64.deb \
 && apt-get update && apt-get install -y ./wkhtml.deb \
 && rm wkhtml.deb

# Copy custom addons
COPY ./custom_addons /mnt/extra-addons

# Install Python dependencies
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy Odoo config and entrypoint
COPY . /mnt/odoo

WORKDIR /mnt/odoo
CMD ["./start.sh"]
