from odoo import api, fields, models
from datetime import datetime
from odoo.exceptions import ValidationError

class RentPayment(models.Model):
    _name = "rent.payment"
    _description = "Rent Payment"

    lease_id = fields.Many2one('property.lease', string='Lease', required=True)
    payment_date = fields.Date(string='Payment Date', required=True)
    
    paid_amount = fields.Monetary(string='Paid Amount', compute='compute_paid_amount', store=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    status = fields.Selection([('paid', 'Paid'), ('unpaid', 'Unpaid')], string='State', required=True)
    note = fields.Text(string='Note')

    @api.depends('lease_id.start_date', 'lease_id.end_date', 'lease_id.monthly_rent')
    def compute_paid_amount(self):
        for record in self:
            lease = record.lease_id
            if lease.start_date and lease.end_date and lease.monthly_rent:
                start = lease.start_date
                end = lease.end_date
                num_months = (end.year - start.year) * 12 + (end.month - start.month) + 1
                record.paid_amount = num_months * lease.monthly_rent
            else:
                record.paid_amount = 0.0

    def _month_start_end(self, date_val):
        month_start = date_val.replace(day=1)
        if month_start.month == 12:
            next_month_start = month_start.replace(year=month_start.year + 1, month=1)
        else:
            next_month_start = month_start.replace(month=month_start.month + 1)
        return month_start, next_month_start

    @api.constrains('lease_id', 'payment_date', 'status')
    def _check_duplicate_payment(self):
        for payment in self:
            if payment.payment_date:
                month_start, next_month_start = self._month_start_end(payment.payment_date)

                # If trying to create a 'paid' record, check for any unpaid or paid record for same lease/month
                if payment.status == 'paid':
                    existing = self.search([
                        ('id', '!=', payment.id),
                        ('lease_id', '=', payment.lease_id.id),
                        ('payment_date', '>=', month_start),
                        ('payment_date', '<', next_month_start),
                        ('status', 'in', ['paid', 'unpaid']),
                    ])
                    if existing:
                        raise ValidationError(
                            "Cannot register a paid rent because there is already a paid or unpaid rent for this lease in the same month."
                        )
                # If trying to create an 'unpaid' record, check for any unpaid or paid record for same lease/month
                elif payment.status == 'unpaid':
                    existing = self.search([
                        ('id', '!=', payment.id),
                        ('lease_id', '=', payment.lease_id.id),
                        ('payment_date', '>=', month_start),
                        ('payment_date', '<', next_month_start),
                        ('status', 'in', ['paid', 'unpaid']),
                    ])
                    if existing:
                        raise ValidationError(
                            "Cannot register an unpaid rent because there is already a paid or unpaid rent for this lease in the same month."
                        )

    def mark_as_paid(self):
        for rec in self:
            if rec.status == 'unpaid' and rec.payment_date:
                month_start, next_month_start = self._month_start_end(rec.payment_date)
                # Check if any paid or unpaid payment exists for same lease and month (excluding self)
                existing = self.search([
                    ('id', '!=', rec.id),
                    ('lease_id', '=', rec.lease_id.id),
                    ('payment_date', '>=', month_start),
                    ('payment_date', '<', next_month_start),
                    ('status', 'in', ['paid', 'unpaid']),
                ])
                if existing:
                    raise ValidationError(
                        "Cannot mark as paid because there is already another rent payment (paid or unpaid) for this lease in the same month."
                    )
                rec.status = 'paid'
