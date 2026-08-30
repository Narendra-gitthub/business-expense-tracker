import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify, Response, redirect, url_for
from models import ExpenseManager, CATEGORIES, PAYMENT_METHODS, STATUSES, format_inr
from sample_data import seed_sample_data

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)
app.config["SECRET_KEY"] = "business-expense-tracker-secret-2026"

DATA_DIR = os.path.join(BASE_DIR, "data")
manager = ExpenseManager(DATA_DIR)

# Auto-seed demo data on first startup
seed_sample_data(DATA_DIR)

@app.context_processor
def inject_global_variables():
    settings = manager.load_settings()
    now_month = datetime.now().strftime("%Y-%m")
    return {
        "categories": CATEGORIES,
        "payment_methods": PAYMENT_METHODS,
        "statuses": STATUSES,
        "settings": settings,
        "current_month_str": now_month,
        "format_inr": format_inr
    }

# ==================== PAGE ROUTES ====================

@app.route("/")
def dashboard():
    month = request.args.get("month", datetime.now().strftime("%Y-%m"))
    summary = manager.get_summary_metrics(month)
    recent_expenses = manager.filter_expenses(month=month)[:6] if month != "all" else manager.load_expenses()[:6]
    return render_template("index.html", summary=summary, recent_expenses=recent_expenses, active_page="dashboard")

@app.route("/expenses")
def expenses_page():
    query = request.args.get("q", "")
    category = request.args.get("category", "All")
    payment_method = request.args.get("payment_method", "All")
    status = request.args.get("status", "All")
    month = request.args.get("month", "All")
    min_amount = request.args.get("min_amount", type=float)
    max_amount = request.args.get("max_amount", type=float)

    filtered = manager.filter_expenses(
        query=query,
        category=category,
        payment_method=payment_method,
        status=status,
        month=month,
        min_amount=min_amount,
        max_amount=max_amount
    )

    total_filtered_amount = sum(float(e.get("amount", 0.0)) for e in filtered)
    
    all_expenses = manager.load_expenses()
    months_set = {str(e.get("date", ""))[:7] for e in all_expenses if len(str(e.get("date", ""))) >= 7}
    months_list = sorted(list(months_set), reverse=True)

    return render_template(
        "expenses.html",
        expenses=filtered,
        total_filtered_amount=total_filtered_amount,
        total_filtered_formatted=format_inr(total_filtered_amount),
        filter_q=query,
        filter_cat=category,
        filter_pm=payment_method,
        filter_status=status,
        filter_month=month,
        filter_min=min_amount,
        filter_max=max_amount,
        available_months=months_list,
        next_id=manager.generate_next_id(),
        today_date=datetime.now().strftime("%Y-%m-%d"),
        active_page="expenses"
    )

@app.route("/reports")
def reports_page():
    month = request.args.get("month", datetime.now().strftime("%Y-%m"))
    summary = manager.get_summary_metrics(month)
    ascii_report = manager.generate_text_report(month)
    return render_template("reports.html", summary=summary, ascii_report=ascii_report, active_page="reports")

@app.route("/settings")
def settings_page():
    settings = manager.load_settings()
    summary = manager.get_summary_metrics()
    return render_template("settings.html", settings=settings, summary=summary, active_page="settings")

# ==================== REST API ENDPOINTS ====================

@app.route("/api/expenses", methods=["GET"])
def api_get_expenses():
    query = request.args.get("q")
    category = request.args.get("category")
    payment_method = request.args.get("payment_method")
    status = request.args.get("status")
    month = request.args.get("month")
    
    results = manager.filter_expenses(
        query=query,
        category=category,
        payment_method=payment_method,
        status=status,
        month=month
    )
    return jsonify({"success": True, "count": len(results), "data": results})

@app.route("/api/expenses", methods=["POST"])
def api_add_expense():
    data = request.get_json() or request.form.to_dict()
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400

    try:
        amount = float(data.get("amount", 0))
        if amount <= 0:
            return jsonify({"success": False, "message": "Amount must be greater than 0"}), 400
    except ValueError:
        return jsonify({"success": False, "message": "Invalid amount number"}), 400

    created = manager.add_expense(data)
    return jsonify({"success": True, "message": "Expense added successfully!", "data": created}), 201

@app.route("/api/expenses/<expense_id>", methods=["GET"])
def api_get_expense(expense_id):
    expense = manager.get_expense_by_id(expense_id)
    if not expense:
        return jsonify({"success": False, "message": "Expense not found"}), 404
    return jsonify({"success": True, "data": expense})

@app.route("/api/expenses/<expense_id>", methods=["PUT", "POST"])
def api_update_expense(expense_id):
    data = request.get_json() or request.form.to_dict()
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400

    updated = manager.update_expense(expense_id, data)
    if not updated:
        return jsonify({"success": False, "message": "Expense not found"}), 404
    return jsonify({"success": True, "message": "Expense updated successfully!", "data": updated})

@app.route("/api/expenses/<expense_id>", methods=["DELETE"])
def api_delete_expense(expense_id):
    deleted = manager.delete_expense(expense_id)
    if not deleted:
        return jsonify({"success": False, "message": "Expense not found"}), 404
    return jsonify({"success": True, "message": "Expense deleted successfully!"})

@app.route("/api/expenses/<expense_id>/status", methods=["PATCH", "POST"])
def api_update_status(expense_id):
    data = request.get_json() or request.form.to_dict()
    new_status = data.get("status")
    if not new_status or new_status not in STATUSES:
        return jsonify({"success": False, "message": "Invalid status"}), 400

    updated = manager.update_expense(expense_id, {"status": new_status})
    if not updated:
        return jsonify({"success": False, "message": "Expense not found"}), 404
    return jsonify({"success": True, "message": f"Status updated to {new_status}", "data": updated})

@app.route("/api/reports/monthly", methods=["GET"])
def api_monthly_metrics():
    month = request.args.get("month", datetime.now().strftime("%Y-%m"))
    summary = manager.get_summary_metrics(month)
    return jsonify({"success": True, "data": summary})

@app.route("/api/settings/budget", methods=["POST"])
def api_update_budget():
    data = request.get_json() or request.form.to_dict()
    try:
        new_budget = float(data.get("monthly_budget", 0))
        if new_budget < 0:
            return jsonify({"success": False, "message": "Budget cannot be negative"}), 400
        
        settings = manager.load_settings()
        settings["monthly_budget"] = new_budget
        if "company_name" in data and data["company_name"]:
            settings["company_name"] = data["company_name"].strip()
            
        manager.save_settings(settings)
        return jsonify({"success": True, "message": "Settings updated successfully!", "data": settings})
    except ValueError:
        return jsonify({"success": False, "message": "Invalid budget value"}), 400

@app.route("/api/export/csv")
def api_export_csv():
    csv_data = manager.export_to_csv()
    filename = f"business_expenses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )

@app.route("/api/export/json")
def api_export_json():
    expenses = manager.load_expenses()
    filename = f"business_expenses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    return Response(
        json.dumps(expenses, indent=2, ensure_ascii=False),
        mimetype="application/json",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )

@app.route("/api/import", methods=["POST"])
def api_import_data():
    if "file" not in request.files:
        return jsonify({"success": False, "message": "No file uploaded"}), 400
        
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"success": False, "message": "No selected file"}), 400
        
    overwrite = request.form.get("overwrite", "false").lower() == "true"
    filename = file.filename.lower()

    try:
        content = file.read().decode("utf-8")
        if filename.endswith(".csv"):
            count = manager.import_from_csv(content, overwrite=overwrite)
            return jsonify({"success": True, "message": f"Successfully imported {count} expenses from CSV!"})
        elif filename.endswith(".json"):
            items = json.loads(content)
            if not isinstance(items, list):
                return jsonify({"success": False, "message": "JSON must be a list of expense objects"}), 400
            
            existing = [] if overwrite else manager.load_expenses()
            existing_ids = {str(e.get("id")).strip() for e in existing}
            added = 0
            
            for item in items:
                exp_id = str(item.get("id", "")).strip()
                if not exp_id or exp_id in existing_ids:
                    exp_id = manager.generate_next_id()
                item["id"] = exp_id
                existing.append(item)
                existing_ids.add(exp_id)
                added += 1
                
            manager.save_expenses(existing)
            return jsonify({"success": True, "message": f"Successfully imported {added} expenses from JSON!"})
        else:
            return jsonify({"success": False, "message": "Only .csv and .json files are supported"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to import file: {str(e)}"}), 500

@app.route("/api/reset-sample", methods=["POST"])
def api_reset_sample():
    from sample_data import SAMPLE_EXPENSES
    manager.save_expenses(list(SAMPLE_EXPENSES))
    settings = manager.load_settings()
    settings["monthly_budget"] = 150000.0
    manager.save_settings(settings)
    return jsonify({"success": True, "message": "Demo sample data reset successfully!"})

if __name__ == "__main__":
    print("==================================================")
    print("   Starting Business Expense Tracker Web App      ")
    print("   URL: http://127.0.0.1:5000                    ")
    print("==================================================")
    app.run(host="0.0.0.0", port=5000, debug=True)
