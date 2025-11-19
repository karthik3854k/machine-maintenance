// Copyright (c) 2025, karthik polisetty and contributors
// For license information, please see license.txt

// Copyright (c) 2025, karthik polisetty and contributors
// For license information, please see license.txt

frappe.query_reports["Machine Maintenance Report"] = {
    "filters": [
        {
            "fieldname": "machine",
            "label": __("Machine"),
            "fieldtype": "Link",
            "options": "Item"
        },
        {
            "fieldname": "technician",
            "label": __("Technician"),
            "fieldtype": "Link",
            "options": "Employee"
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date"
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date"
        },
        {
            "fieldname": "consolidated",
            "label": __("Consolidated"),
            "fieldtype": "Check",
            "default": 0
        }
    ],

    formatter: function (value, row, column, data, default_formatter) {

        value = default_formatter(value, row, column, data);

        if (!data) return value;
        if (data.status === "Consolidated") {
            return value;
        }

        let status = data.status;

        if (status === "Overdue") {
            return `<span style="background-color:#ffcccc; display:block;">${value}</span>`;
        }
        if (status === "Scheduled") {
            return `<span style="background-color:#fff3cd; display:block;">${value}</span>`;
        }
        if (status === "Completed") {
            return `<span style="background-color:#d4edda; display:block;">${value}</span>`;
        }

        return value;
    }
};
