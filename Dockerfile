FROM python:3.10

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git build-essential python3-dev libldap2-dev libsasl2-dev libpq-dev wkhtmltopdf \
    && rm -rf /var/lib/apt/lists/*

# Clone Odoo core
RUN git clone --depth=1 --branch 18.0 https://github.com/odoo/odoo.git /odoo

# Copy your custom modules
COPY . /mnt/extra-addons

# Install Python dependencies
RUN pip install -r /odoo/requirements.txt

# Expose Odoo port
EXPOSE 8069

# Set entrypoint
CMD ["python", "/odoo/odoo-bin", "--addons-path=/odoo/addons,/mnt/extra-addons", "--db_host=$DB_HOST", "--db_port=$DB_PORT", "--db_user=$DB_USER", "--db_password=$DB_PASSWORD"]
