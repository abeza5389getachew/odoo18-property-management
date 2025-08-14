from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import timedelta, date
import io
import xlsxwriter
from odoo.http import content_disposition, request
from odoo import http


class Lease(models.Model):
    _name = 'property.lease'
    _description = 'Property Lease'
    _order = 'start_date desc'

    lease_name = fields.Char(string="Lease Name", compute='_compute_lease_name', store=True)
    tenant_id = fields.Many2one('property.tenant', string='Tenant', required=True)
    property_id = fields.Many2one('property.management', string='Property', required=True)
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    monthly_rent = fields.Float(string="Monthly Rent", required=True)
    total_paid_amount = fields.Float(string = "Total Paid Amount", compute = '_compute_total_paid_amount', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired')
    ], string='Status', default='draft')

    lease_pdf = fields.Binary('PDF')
    rent_payment_ids = fields.One2many('rent.payment', 'lease_id', string='Rent Payments')

    # ------------------------------
    # Compute Lease Name
    # ------------------------------
    @api.depends('tenant_id', 'property_id')
    def _compute_lease_name(self):
        for rec in self:
            if rec.tenant_id and rec.property_id:
                rec.lease_name = f"{rec.tenant_id.name} - {rec.property_id.name}"
            else:
                rec.lease_name = "Lease"

    #compute total paid amount
    @api.depends('start_date', 'end_date', 'monthly_rent')
    def _compute_total_paid_amount(self):
        for record in self:
            if record.start_date and record.end_date and record.monthly_rent:
                num_months = ((record.end_date.year - record.start_date.year) * 12 +
                              (record.end_date.month - record.start_date.month) + 1)
                record.total_paid_amount = num_months * record.monthly_rent
            else:
                record.total_paid_amount = 0.0

    # ------------------------------
    # Onchange: Auto-fill rent from property
    # ------------------------------
    @api.onchange('property_id')
    def _onchange_property_id(self):
        if self.property_id:
            self.monthly_rent = self.property_id.price_per_month

    # ------------------------------
    # Constraint: Start date < End date
    # ------------------------------
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for rec in self:
            if rec.start_date and rec.end_date and rec.end_date <= rec.start_date:
                raise ValidationError("End date must be after start date")

    # ------------------------------
    # Constraint: Avoid overlapping leases
    # ------------------------------
    @api.constrains('property_id', 'start_date', 'end_date', 'state')
    def _check_property_overlap_or_expire(self):
        for rec in self:
            if rec.property_id and rec.start_date and rec.end_date:
                overlapping_leases = self.search([
                    ('id', '!=', rec.id),
                    ('property_id', '=', rec.property_id.id),
                    ('state', 'in', ['draft', 'active']),
                ])
                for lease in overlapping_leases:
                    if lease.start_date <= rec.end_date and lease.end_date >= rec.start_date:
                        raise ValidationError(
                            f"The property '{rec.property_id.name}' already has another lease "
                            f"({lease.lease_name}) during the selected period."
                        )
                    if lease.end_date == rec.start_date - timedelta(days=1) and lease.state == 'active':
                        lease.state = 'expired'

    # ------------------------------
    # Reminder: Send expiry notifications
    # ------------------------------
    def _send_lease_expiry_reminders(self):
        today = date.today()
        reminder_date = today + timedelta(days=30)

        leases = self.search([
            ('state', '=', 'active'),
            ('end_date', '=', reminder_date)
        ])

        for lease in leases:
            lease.tenant_id.partner_id.message_post(
                body=f"Reminder: The lease '{lease.lease_name}' for property '{lease.property_id.name}' "
                     f"will expire on {lease.end_date}. Please take necessary action."
            )

    # ------------------------------
    # Override create: Mark property rented
    # ------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            record.property_id.status = 'rented'
        return records

    # ------------------------------
    # Expire Lease Action
    # ------------------------------
    def expire_lease(self):
        for rec in self:
            if rec.end_date < fields.Date.today():
                rec.state = 'expired'

    # ------------------------------
    # QWeb PDF Report
    # ------------------------------
    def print_lease_summary_report(self):
        return self.env.ref('property_management.action_lease_summary_report').report_action(self)

    # ------------------------------
    # XLSX Export Action - returns URL for download
    # ------------------------------
    def export_xlsx(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/lease/xlsx_all',
            'target': 'self',
        }


# ------------------------------
# HTTP Controller for XLSX download of all leases
# ------------------------------
class LeaseXlsxController(http.Controller):
    @http.route('/lease/xlsx_all', type='http', auth='user')
    def download_xlsx_all(self, **kwargs):
        leases = request.env['property.lease'].search([])
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Leases')

        headers = ['Lease Name', 'Tenant', 'Property', 'Start Date', 'End Date', 'Monthly Rent','total_paid_amount', 'Status']
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC'})
        date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})

        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)

        row = 1
        for lease in leases:
            worksheet.write(row, 0, lease.lease_name or '')
            worksheet.write(row, 1, lease.tenant_id.name or '')
            worksheet.write(row, 2, lease.property_id.name or '')
            if lease.start_date:
                worksheet.write_datetime(row, 3, lease.start_date, date_format)
            else:
                worksheet.write(row, 3, '')
            if lease.end_date:
                worksheet.write_datetime(row, 4, lease.end_date, date_format)
            else:
                worksheet.write(row, 4, '')
            worksheet.write(row, 5, lease.monthly_rent or 0.0)
            worksheet.write(row, 6, lease.total_paid_amount or 0.0)
            worksheet.write(row, 7, lease.state or '')
            row += 1

        workbook.close()
        output.seek(0)

        return request.make_response(
            output.read(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', content_disposition('lease_summary_report.xlsx'))
            ]
        )
