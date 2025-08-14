{
    "name": "Property Management",
    "author": "Abeza Getachew",
    "license": "LGPL-3",
    "summary": "Module for property and rental management",
    "category": "Real Estate",
    "description": "A complete solution to manage properties, leases, tenants, and rent payments in Odoo.",
    "version": "18.0.1.0",
    "depends": ["base", "web"],
    "sequence": 0,
    "data": [
         "data/cron.xml",
         "security/security.xml",
         "security/ir.model.access.csv",
         "views/property_views.xml",
         "views/tenant_views.xml",
         "views/lease_views.xml",
         "views/rent_payment_views.xml",
         "views/menu.xml",
         "views/lease_report.xml",
         "views/lease_report_templates.xml"
    ],
    "installable": True,
    "auto_install": False,
    "application": True
}