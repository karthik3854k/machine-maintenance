// Copyright (c) 2025, karthik polisetty and contributors
// For license information, please see license.txt

frappe.ui.form.on("Machine Maintenance", {
    refresh(frm) {
        frm.trigger("toggle_notes_visibility");

        if (!frm.is_new() && frm.doc.docstatus === 0) {
            frm.add_custom_button(__("Mark Completed"), function () {
                frm.set_value("status", "Completed");
                if (!frm.doc.completion_date) {
                    frm.set_value("completion_date", frappe.datetime.get_today());
                }
                frm.save();
            }, __("Actions"));
        }
    },

    onload(frm) {
        if (frm.is_new() && !frm.doc.maintenance_date) {
            frm.set_value("maintenance_date", frappe.datetime.get_today());
        }
    },

    status(frm) {
        frm.trigger("toggle_notes_visibility");
    },

    maintenance_date(frm) {
        const today = frappe.datetime.get_today();
        if (frm.doc.maintenance_date && frm.doc.status !== "Completed") {
            if (frm.doc.maintenance_date < today) {
                frm.set_value("status", "Overdue");
            }
        }
    },

    toggle_notes_visibility(frm) {
        const hide_notes = frm.doc.status === "Scheduled";
        frm.toggle_display("notes", !hide_notes);
    }
});

frappe.ui.form.on("Machine Maintenance Part", {
    quantity(frm, cdt, cdn) {
        update_amount(cdt, cdn);
    },
    rate(frm, cdt, cdn) {
        update_amount(cdt, cdn);
    }
});

function update_amount(cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    row.amount = (row.quantity || 0) * (row.rate || 0);
    frappe.model.set_value(cdt, cdn, "amount", row.amount);
}
