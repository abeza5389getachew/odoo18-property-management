from odoo import api, fields, models

class PropertyManagement(models.Model):
    _name = 'property.management'
    _description = 'Propery management'

    name = fields.Char(string='Name', required= True)
    property_type = fields.Selection([('apartement', 'Apartement'), ('villa', 'Villa'),('office','Office')], string='Propert Type', required= True)
    price_per_month = fields.Float(string='Price per month', required= True)
    status = fields.Selection([('available', 'Available'), ('rented', 'Rented'), ('maintenance', 'Maintainance')], string = 'Status', required= True)
    image = fields.Image(string="Image", required= True)
    description = fields.Text(string='Description')


    
