from odoo import models, fields

class ExpenseApprover(models.Model):
    _name = "expense.approver"
    _description = "Expense Approver Line"

    expense_id = fields.Many2one('expense.request', ondelete='cascade', required=True)
    approver_id = fields.Many2one('res.users', string='Approver', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    approved = fields.Boolean(string='Approved', default=False)
    comment = fields.Text()
