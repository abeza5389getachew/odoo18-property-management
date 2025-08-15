FROM python:3.10-slim

# Install system dependencies and libssl1.1 manually
RUN apt-get update && apt-get install -y \
    git build-essential python3-dev libldap2-dev libsasl2-dev libpq-dev curl fontconfig libxrender1 libxext6 xfonts-75dpi xfonts-base \
    && curl -o /tmp/libssl1.1.deb -SL http://security.debian.org/debian-security/pool/updates/main/o/openssl/libssl1.1_1.1.1w-0+deb11u1_amd64.deb \
    && apt install -y /tmp/libssl1.1.deb \
    && rm /tmp/libssl1.1.deb \
    && curl -o /tmp/wkhtml.deb -SL https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_amd64.deb \
    && apt install -y /tmp/wkhtml.deb \
    && rm /tmp/wkhtml.deb \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /mnt/extra-addons

# Copy custom addons
COPY ./custom_addons/property_management /mnt/extra-addons/property_management
# Install Odoo
RUN pip install wheel setuptools \
    && pip install odoo==18.0

# Set environment variables
ENV ODOO_RC=/etc/odoo/odoo.conf
ENV ADDONS_PATH=/mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons

# Expose Odoo port
EXPOSE 8069

# Default command
CMD ["odoo", "-c", "/etc/odoo/odoo.conf"]

