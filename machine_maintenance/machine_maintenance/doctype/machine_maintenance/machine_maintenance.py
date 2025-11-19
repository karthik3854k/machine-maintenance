# Copyright (c) 2025, karthik polisetty and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate, flt
from erpnext.accounts.doctype.journal_entry.journal_entry import (
    get_default_bank_cash_account,
)
from erpnext.setup.utils import get_exchange_rate


class MachineMaintenance(Document):

    def validate(self):
        self.set_default_values()
        self.calculate_parts_amount()
        self.calculate_total_cost()
        self.validate_dates()
        self.set_overdue_status_if_needed()
        self.validate_technician_presence_when_needed()

    def set_default_values(self):
        if not self.maintenance_date:
            self.maintenance_date = today()

        if not self.status:
            self.status = "Draft"

        if self.company and not self.currency:
            self.currency = frappe.db.get_value("Company", self.company, "default_currency")

    def calculate_parts_amount(self):
        """Amount = qty * rate in child table."""
        for row in self.parts_used or []:
            row.quantity = flt(row.quantity)
            row.rate = flt(row.rate)
            row.amount = row.quantity * row.rate

    def calculate_total_cost(self):
        """Cost = sum of all parts_used.amount"""
        total = 0.0
        for row in self.parts_used or []:
            total += flt(row.amount)
        self.cost = total

    def validate_dates(self):
        if self.maintenance_date and self.completion_date:
            if getdate(self.completion_date) < getdate(self.maintenance_date):
                frappe.throw("Completion Date cannot be before Maintenance Date.")

    def set_overdue_status_if_needed(self):
        """Auto mark as Overdue if Maintenance Date < today and not Completed/Closed."""
        if self.maintenance_date and self.status not in ["Completed", "Closed"]:
            if getdate(self.maintenance_date) < getdate(today()):
                self.status = "Overdue"

    def validate_technician_presence_when_needed(self):
        """Extra validation: Require technician for Scheduled/Completed/Overdue/Closed."""
        if self.status in ["Scheduled", "Completed", "Overdue", "Closed"] and not self.technician:
            frappe.throw("Technician must be assigned before setting status to {}."
                         .format(self.status))

    def on_submit(self):
        if not self.technician:
            frappe.throw("Technician must be assigned before submitting Machine Maintenance.")

        if not self.company:
            frappe.throw("Company is mandatory to create the Journal Entry.")

        if not self.cost or self.cost <= 0:
            frappe.throw("Cost should be greater than zero before submitting.")

        self.make_journal_entry()

    def make_journal_entry(self):
        """Create Journal Entry for maintenance cost:
           Debit: Maintenance Expense
           Credit: Cash/Bank
        """
        company_currency = frappe.db.get_value("Company", self.company, "default_currency")
        if not company_currency:
            frappe.throw("Default currency not set for Company {}.".format(self.company))

        if not self.currency:
            self.currency = company_currency

        posting_date = self.completion_date or self.maintenance_date or today()


        exchange_rate = 1.0
        if self.currency != company_currency:
            exchange_rate = get_exchange_rate(self.currency, company_currency, posting_date)

        base_amount = flt(self.cost) * flt(exchange_rate)


        maintenance_expense_account = frappe.db.get_value(
            "Company", self.company, "default_expense_account"
        )
        if not maintenance_expense_account:
            frappe.throw("Please set Default Expense Account in Company {}."
                         .format(self.company))

  
        bank_cash = get_default_bank_cash_account(self.company)
        if not bank_cash or not bank_cash.get("account"):
            frappe.throw("Please configure a default Cash/Bank account for company {}."
                         .format(self.company))

        je = frappe.new_doc("Journal Entry")
        je.voucher_type = "Journal Entry"
        je.posting_date = posting_date
        je.company = self.company
        je.user_remark = "Machine Maintenance for {} ({}).".format(
            self.machine_name or "", self.name
        )

  
        je.append("accounts", {
            "account": maintenance_expense_account,
            "debit_in_account_currency": self.cost,
            "debit": base_amount,
            "exchange_rate": exchange_rate,
            "reference_type": self.doctype,
            "reference_name": self.name,
        })


        je.append("accounts", {
            "account": bank_cash.account,
            "credit_in_account_currency": self.cost,
            "credit": base_amount,
            "exchange_rate": exchange_rate,
            "reference_type": self.doctype,
            "reference_name": self.name,
        })

        je.flags.ignore_permissions = True
        je.insert()
        je.submit()

        self.journal_entry = je.name
        frappe.msgprint("Journal Entry {} created for maintenance cost.".format(je.name))

