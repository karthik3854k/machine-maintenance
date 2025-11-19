# Copyright (c) 2025, karthik polisetty and contributors
# For license information, please see license.txt


import frappe
from frappe.utils import flt

def execute(filters=None):
    filters = filters or {}

    consolidated = bool(filters.get("consolidated"))
    columns = get_columns(consolidated)
    data = get_data(filters, consolidated)

    return columns, data


# -------------------------------------------------------
# Columns
# -------------------------------------------------------
def get_columns(consolidated):
    cols = [
        {
            "label": "Machine",
            "fieldname": "machine_name",
            "fieldtype": "Link",
            "options": "Item",
            "width": 200,
        }
    ]

    if not consolidated:
        cols += [
            {
                "label": "Maintenance Date",
                "fieldname": "maintenance_date",
                "fieldtype": "Date",
                "width": 110,
            },
            {
                "label": "Technician",
                "fieldname": "technician",
                "fieldtype": "Link",
                "options": "Employee",
                "width": 150,
            },
            {
                "label": "Status",
                "fieldname": "status",
                "fieldtype": "Data",
                "width": 110,
            },
        ]
    else:
        # Only show grouped status column
        cols.append({
            "label": "Status",
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 110,
        })

    # Common column
    cols.append({
        "label": "Total Cost",
        "fieldname": "total_cost",
        "fieldtype": "Currency",
        "width": 140,
    })

    return cols


# -------------------------------------------------------
# SQL Filters
# -------------------------------------------------------
def get_conditions(filters):
    conditions = ["docstatus = 1"]
    values = {}

    if filters.get("machine"):
        conditions.append("machine_name = %(machine)s")
        values["machine"] = filters["machine"]

    if filters.get("technician"):
        conditions.append("technician = %(technician)s")
        values["technician"] = filters["technician"]

    if filters.get("from_date"):
        conditions.append("maintenance_date >= %(from_date)s")
        values["from_date"] = filters["from_date"]

    if filters.get("to_date"):
        conditions.append("maintenance_date <= %(to_date)s")
        values["to_date"] = filters["to_date"]

    return " AND ".join(conditions), values


# -------------------------------------------------------
# Fetch Data
# -------------------------------------------------------
def get_data(filters, consolidated):
    conditions, values = get_conditions(filters)

    if consolidated:
        query = f"""
            SELECT
                machine_name,
                'Consolidated' AS status,
                SUM(cost) AS total_cost
            FROM `tabMachine Maintenance`
            WHERE {conditions}
            GROUP BY machine_name
            ORDER BY machine_name
        """
    else:
        query = f"""
            SELECT
                machine_name,
                maintenance_date,
                technician,
                status,
                cost AS total_cost
            FROM `tabMachine Maintenance`
            WHERE {conditions}
            ORDER BY maintenance_date DESC, machine_name
        """

    rows = frappe.db.sql(query, values, as_dict=True)

    # Ensure cost always numeric
    for row in rows:
        row["total_cost"] = flt(row.get("total_cost"))

    return rows
