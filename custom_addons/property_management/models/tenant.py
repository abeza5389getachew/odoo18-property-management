from odoo import api, fields,models
from odoo.exceptions import ValidationError
import re

class PropertyTenant(models.Model):
    _name = 'property.tenant'
    _description = 'a tenant for apartement'

    name = fields.Char(string='Name', required= True)
    email=fields.Char(string='Email', required = True)
    phone=fields.Char(string ='Phone', required = True)
    id_number=fields.Char(string ='Id Number', required = True)

    lease_ids = fields.One2many('property.lease', 'tenant_id', string='Leases')

    # @api.constrains('phone')
    # def _check_phone_number(self):
    #     for record in self:
    #         ethio_phone_regex = r'^((\+2519\d{8})|(09\d{8}))$'
    #         if record.phone and not re.match(ethio_phone_regex, record.phone):
    #             raise ValidationError("Phone number must be Ethiopian format")
            
    # #check phone number
    # @api.constrains('phone')
    # def _check_phone_number(self):
    #     for record in self:
    #         phone_num = record.phone
    #         pattern = r'^\+251[79]\d{8}$'
    #         if not re.match( pattern,phone_num):
    #             raise ValidationError("please enter a valid phone number")
            
    # @api.model
    # def create(self, vals):
    #     vals['phone'] = self._format_phone(vals.get('phone'))
    #     return super().create(vals)
    
    # #update if error occure
    # def write(self, vals):
    #  if 'phone' in vals:
    #      vals['phone'] = self._format_phone(vals.get('phone'))
    #  return super().write(vals)
    # #format phone from 09 to +251
    # def _format_phone(self, phone_num):
    #     if phone_num and not phone_num.startswith('+251'):
    #        if re.fullmatch(r'[79]\d{8}', phone_num ):
    #             return '+251' + phone_num
    #     return phone_num
    
    # @api.constrains('phone')
    # def _check_phone_number(self):
    #     for record in self:
    #         phone_num = record.phone
    #         pattern = r'^\+251[79]\d{8}$'
    #         if not re.match( pattern,phone_num):
    #             raise ValidationError("please enter a valid phone number")
    
    def _format_phone(self, phone_num):
            if phone_num and not phone_num.startswith('+251'):
                if re.fullmatch(r'0[79]\d{8}', phone_num):
                    return '+251' + phone_num[1:]
            return phone_num

    def _check_phone_number(self):
        for record in self:
            pattern = r'^\+251[79]\d{8}$'
            if not re.match(pattern, record.phone):
                raise ValidationError("Please enter a valid Ethiopian phone number (e.g., 0912345678 or +251912345678)")

    @api.model
    def create(self, vals):
        if 'phone' in vals:
            vals['phone'] = self._format_phone(vals.get('phone'))
        record = super().create(vals)
        record._check_phone_number()
        return record

    def write(self, vals):
        if 'phone' in vals:
            vals['phone'] = self._format_phone(vals.get('phone'))
        res = super().write(vals)
        self._check_phone_number()
        return res

    #validate email
    @api.constrains('email')
    def _check_email(self):
        for record in self:
            email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
            if record.email and not re.match(email_regex, record.email):
                raise ValidationError("Email format is invalid.")
