{
    "name": "Expense Approval - Hackathon",
    "version": "1.0",
    "summary": "Multi-level expense approvals with conditional rules and currency support",
    "category": "Human Resources",
    "depends": ["base", "mail", "hr"],
    "data": [
        "security/ir.model.access.csv",
        "views/expense_views.xml",
        # "data/demo_users.xml",  # optional
    ],
    "installable": True,
    "application": False,
}
