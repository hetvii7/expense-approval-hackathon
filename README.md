# Expense Approval - Hackathon
Short: Odoo addon implementing multi-level expense approvals with conditional rules and currency support.

## Install
1. Add `addons/expense_approval` to your Odoo addons_path.
2. Restart Odoo and update Apps list.
3. Install "Expense Approval - Hackathon".

## Demo users
- Admin: <create via Odoo UI>
- Manager: <create via Odoo UI>
- Employee: <create via Odoo UI>

## Run
1. Create Employee expense -> add approver lines -> Submit.
2. Approvers approve in order; conditional rules apply (specific / percentage).
3. See messages in chatter.

## Known limitations
- OCR is a demo-stub (Auto-fill). Real OCR (pytesseract) can be wired later.
- Currency rates use Odoo `res.currency` convert; external API fallback optional.

## Video
<paste your final demo link here>
