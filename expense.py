from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests

class ExpenseRequest(models.Model):
    _name = "expense.request"
    _description = "Expense Request"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Reference", default=lambda s: "EXP")
    employee_id = fields.Many2one('hr.employee', string='Employee')
    user_id = fields.Many2one('res.users', string='Submitter', default=lambda self: self.env.user)
    amount = fields.Float(string='Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id.id)
    date = fields.Date(default=fields.Date.context_today)
    category = fields.Selection([('travel','Travel'),('meals','Meals'),('office','Office')], default='travel')
    description = fields.Text()
    state = fields.Selection([
        ('draft','Draft'),
        ('to_approve','To Approve'),
        ('approved','Approved'),
        ('rejected','Rejected')
    ], default='draft', tracking=True)

    approver_line_ids = fields.One2many('expense.approver', 'expense_id', string='Approvers', copy=True)
    approval_rule = fields.Selection([('percentage','Percentage'),('specific','Specific'),('hybrid','Hybrid')], default='percentage')
    percentage_threshold = fields.Integer(string='Threshold (%)', default=60)
    specific_approver_id = fields.Many2one('res.users', string='Specific approver')

    company_currency_amount = fields.Monetary(string='Amount (Company Currency)', compute='_compute_company_amount', store=False)
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.depends('amount','currency_id')
    def _compute_company_amount(self):
        for rec in self:
            try:
                rec.company_currency_amount = rec._convert_to_company_currency(rec.amount, rec.currency_id, rec.company_id.currency_id)
            except Exception:
                rec.company_currency_amount = rec.amount

    def _convert_to_company_currency(self, amount, from_currency, to_currency):
        # Simple approach: use Odoo currency conversion if available
        if not from_currency or not to_currency or from_currency == to_currency:
            return amount
        return self.env['res.currency']._convert(amount, from_currency, to_currency, self.company_id, self.date or fields.Date.today())

    def action_submit(self):
        for rec in self:
            if not rec.approver_line_ids:
                raise UserError("Please assign at least one approver before submitting.")
            rec.state = 'to_approve'
            # notify first approver
            first = rec._get_next_approver_line()
            if first:
                partner = first.approver_id.partner_id
                rec.message_post(body=f"Approval requested for {rec.name}", partner_ids=[partner.id])

    def _get_next_approver_line(self):
        self.ensure_one()
        pending = self.approver_line_ids.filtered(lambda l: not l.approved)
        if not pending:
            return False
        return pending.sorted(key=lambda r: r.sequence)[0]

    def action_approve(self, comment=''):
        for rec in self:
            current_line = rec.approver_line_ids.filtered(lambda l: l.approver_id == self.env.user and not l.approved)
            if not current_line:
                raise UserError("You are not the current approver or already approved.")
            current_line.approved = True
            current_line.comment = comment
            # specific approver rule
            if rec.approval_rule in ('specific','hybrid') and rec.specific_approver_id and rec.specific_approver_id == self.env.user:
                rec.state = 'approved'
                rec.message_post(body="Approved (specific approver)")
                continue
            # percentage rule
            total = len(rec.approver_line_ids)
            approved = len(rec.approver_line_ids.filtered(lambda l: l.approved))
            if total > 0 and (approved / total) * 100 >= rec.percentage_threshold:
                rec.state = 'approved'
                rec.message_post(body="Approved by percentage rule")
                continue
            # otherwise notify next approver
            next_line = rec._get_next_approver_line()
            if not next_line:
                # no more approvers -> approve
                rec.state = 'approved'
                rec.message_post(body="Approved (end of workflow)")
            else:
                rec.message_post(body="Approval requested", partner_ids=[next_line.approver_id.partner_id.id])

    def action_reject(self, comment=''):
        for rec in self:
            current_line = rec.approver_line_ids.filtered(lambda l: l.approver_id == self.env.user and not l.approved)
            if not current_line:
                raise UserError("You are not the current approver or already acted.")
            current_line.comment = comment
            rec.state = 'rejected'
            rec.message_post(body=f"Rejected: {comment}")
