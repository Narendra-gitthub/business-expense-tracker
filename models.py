import os
import json
import csv
import io
from datetime import datetime
from typing import List, Dict, Any, Optional

CATEGORIES = [
    "Office Supplies",
    "Rent",
    "Electricity",
    "Transportation",
    "Marketing",
    "Salaries",
    "Equipment",
    "Software/Subscriptions",
    "Travel",
    "Miscellaneous"
]

PAYMENT_METHODS = [
    "UPI",
    "Bank Transfer",
    "Credit/Debit Card",
    "Cash"
]

STATUSES = [
    "Pending",
    "Paid",
    "Reimbursed"
]

def format_inr(number: float) -> str:
    """Format number as Indian Rupee string, e.g. 124500 -> ₹1,24,500"""
    try:
        num = round(float(number), 2)
        is_negative = num < 0
        num = abs(num)
        
        parts = f"{num:.2f}".split(".")
        int_part = parts[0]
        dec_part = parts[1]
        
        if len(int_part) <= 3:
            formatted_int = int_part
        else:
            last_three = int_part[-3:]
            remaining = int_part[:-3]
            groups = []
            while len(remaining) > 2:
                groups.insert(0, remaining[-2:])
                remaining = remaining[:-2]
            if remaining:
                groups.insert(0, remaining)
            formatted_int = ",".join(groups) + "," + last_three
            
        sign = "-" if is_negative else ""
        if dec_part == "00":
            return f"{sign}₹{formatted_int}"
        return f"{sign}₹{formatted_int}.{dec_part}"
    except Exception:
        return f"₹{number}"

class ExpenseManager:
    def __init__(self, data_dir: str):
        # On Vercel / serverless, application root is read-only.
        # We redirect persistent file writes to /tmp/expense_tracker_data
        if os.environ.get("VERCEL"):
            self.data_dir = "/tmp/expense_tracker_data"
            os.makedirs(self.data_dir, exist_ok=True)
            bundled_expenses = os.path.join(data_dir, "expenses.json")
            bundled_settings = os.path.join(data_dir, "settings.json")
            target_expenses = os.path.join(self.data_dir, "expenses.json")
            target_settings = os.path.join(self.data_dir, "settings.json")
            
            if os.path.exists(bundled_expenses) and not os.path.exists(target_expenses):
                import shutil
                shutil.copy2(bundled_expenses, target_expenses)
            if os.path.exists(bundled_settings) and not os.path.exists(target_settings):
                import shutil
                shutil.copy2(bundled_settings, target_settings)
        else:
            self.data_dir = data_dir
            os.makedirs(self.data_dir, exist_ok=True)

        self.expenses_file = os.path.join(self.data_dir, "expenses.json")
        self.settings_file = os.path.join(self.data_dir, "settings.json")
        self._ensure_files()

    def _ensure_files(self):
        """Ensure storage files exist with initial content if missing."""
        if not os.path.exists(self.expenses_file):
            with open(self.expenses_file, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)
                
        if not os.path.exists(self.settings_file):
            default_settings = {
                "monthly_budget": 150000.0,
                "currency_symbol": "₹",
                "company_name": "Royal Enterprise",
                "categories": CATEGORIES,
                "payment_methods": PAYMENT_METHODS,
                "statuses": STATUSES
            }
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(default_settings, f, indent=2)

    def load_expenses(self) -> List[Dict[str, Any]]:
        """Load all expenses from JSON storage file."""
        try:
            if not os.path.exists(self.expenses_file):
                return []
            with open(self.expenses_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return sorted(data, key=lambda x: (str(x.get("date", "")), str(x.get("id", ""))), reverse=True)
        except Exception as e:
            print(f"Error loading expenses: {e}")
            return []

    def save_expenses(self, expenses: List[Dict[str, Any]]) -> bool:
        """Persist expenses list to JSON file."""
        try:
            with open(self.expenses_file, "w", encoding="utf-8") as f:
                json.dump(expenses, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving expenses: {e}")
            return False

    def load_settings(self) -> Dict[str, Any]:
        """Load application settings."""
        try:
            if not os.path.exists(self.settings_file):
                self._ensure_files()
            with open(self.settings_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"monthly_budget": 150000.0, "currency_symbol": "₹", "company_name": "My Business"}

    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """Save application settings."""
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False

    def generate_next_id(self) -> str:
        """Generate next numerical ID, e.g. 101, 102, 103..."""
        expenses = self.load_expenses()
        max_num = 100
        for exp in expenses:
            exp_id = str(exp.get("id", ""))
            digits = "".join(filter(str.isdigit, exp_id))
            if digits:
                max_num = max(max_num, int(digits))
        return str(max_num + 1)

    def add_expense(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new expense record."""
        expenses = self.load_expenses()
        
        exp_id = str(data.get("id", "")).strip()
        if not exp_id:
            exp_id = self.generate_next_id()
        else:
            if any(str(x.get("id")).strip() == exp_id for x in expenses):
                exp_id = self.generate_next_id()

        date_val = data.get("date") or datetime.now().strftime("%Y-%m-%d")
        amount_val = float(data.get("amount", 0.0))
        
        new_expense = {
            "id": exp_id,
            "date": date_val,
            "category": data.get("category", "Miscellaneous"),
            "description": data.get("description", "").strip(),
            "amount": amount_val,
            "payment_method": data.get("payment_method", "Cash"),
            "status": data.get("status", "Paid"),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        expenses.append(new_expense)
        self.save_expenses(expenses)
        return new_expense

    def update_expense(self, expense_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing expense by ID."""
        expenses = self.load_expenses()
        updated = None
        expense_id_str = str(expense_id).strip()

        for exp in expenses:
            if str(exp.get("id")).strip() == expense_id_str:
                if "date" in data:
                    exp["date"] = data["date"]
                if "category" in data:
                    exp["category"] = data["category"]
                if "description" in data:
                    exp["description"] = data["description"].strip()
                if "amount" in data:
                    exp["amount"] = float(data["amount"])
                if "payment_method" in data:
                    exp["payment_method"] = data["payment_method"]
                if "status" in data:
                    exp["status"] = data["status"]
                exp["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                updated = exp
                break

        if updated:
            self.save_expenses(expenses)
        return updated

    def delete_expense(self, expense_id: str) -> bool:
        """Delete an expense by ID."""
        expenses = self.load_expenses()
        expense_id_str = str(expense_id).strip()
        initial_len = len(expenses)
        expenses = [exp for exp in expenses if str(exp.get("id")).strip() != expense_id_str]
        if len(expenses) < initial_len:
            self.save_expenses(expenses)
            return True
        return False

    def get_expense_by_id(self, expense_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve single expense by ID."""
        expenses = self.load_expenses()
        expense_id_str = str(expense_id).strip()
        for exp in expenses:
            if str(exp.get("id")).strip() == expense_id_str:
                return exp
        return None

    def filter_expenses(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        payment_method: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        month: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Filter expenses based on multiple search and filter parameters."""
        expenses = self.load_expenses()
        results = []

        for exp in expenses:
            if query:
                q = query.lower().strip()
                exp_id = str(exp.get("id", "")).lower()
                cat = str(exp.get("category", "")).lower()
                desc = str(exp.get("description", "")).lower()
                if q not in exp_id and q not in cat and q not in desc:
                    continue

            if category and category != "All":
                if exp.get("category") != category:
                    continue

            if payment_method and payment_method != "All":
                if exp.get("payment_method") != payment_method:
                    continue

            if status and status != "All":
                if exp.get("status") != status:
                    continue

            exp_date = str(exp.get("date", ""))
            if month and month != "All":
                if not exp_date.startswith(month):
                    continue

            if start_date and exp_date < start_date:
                continue
            if end_date and exp_date > end_date:
                continue

            amount = float(exp.get("amount", 0.0))
            if min_amount is not None and amount < min_amount:
                continue
            if max_amount is not None and amount > max_amount:
                continue

            results.append(exp)

        return results

    def get_summary_metrics(self, month: Optional[str] = None) -> Dict[str, Any]:
        """Compute aggregate metrics, category-wise breakdown, payment breakdowns, and budget status."""
        expenses = self.load_expenses()
        settings = self.load_settings()
        monthly_budget = float(settings.get("monthly_budget", 150000.0))

        current_month = month or datetime.now().strftime("%Y-%m")
        if current_month == "all":
            month_expenses = expenses
            month_display = "All Time"
        else:
            month_expenses = [e for e in expenses if str(e.get("date", "")).startswith(current_month)]
            try:
                month_display = datetime.strptime(current_month, "%Y-%m").strftime("%B %Y")
            except Exception:
                month_display = current_month

        total_all_time = sum(float(e.get("amount", 0.0)) for e in expenses)
        total_month = sum(float(e.get("amount", 0.0)) for e in month_expenses)

        category_totals = {cat: 0.0 for cat in CATEGORIES}
        for e in month_expenses:
            cat = e.get("category", "Miscellaneous")
            category_totals[cat] = category_totals.get(cat, 0.0) + float(e.get("amount", 0.0))

        sorted_categories = sorted(
            [{"category": k, "amount": v, "formatted": format_inr(v), "percentage": round((v / total_month * 100), 1) if total_month > 0 else 0.0} 
             for k, v in category_totals.items() if v > 0],
            key=lambda x: x["amount"],
            reverse=True
        )

        payment_totals = {pm: 0.0 for pm in PAYMENT_METHODS}
        for e in month_expenses:
            pm = e.get("payment_method", "Cash")
            payment_totals[pm] = payment_totals.get(pm, 0.0) + float(e.get("amount", 0.0))

        sorted_payments = [
            {"method": k, "amount": v, "formatted": format_inr(v), "percentage": round((v / total_month * 100), 1) if total_month > 0 else 0.0}
            for k, v in payment_totals.items()
        ]

        status_counts = {"Pending": 0, "Paid": 0, "Reimbursed": 0}
        status_totals = {"Pending": 0.0, "Paid": 0.0, "Reimbursed": 0.0}
        for e in month_expenses:
            st = e.get("status", "Paid")
            status_counts[st] = status_counts.get(st, 0) + 1
            status_totals[st] = status_totals.get(st, 0.0) + float(e.get("amount", 0.0))

        top_category = sorted_categories[0]["category"] if sorted_categories else "None"
        top_category_amount = sorted_categories[0]["amount"] if sorted_categories else 0.0

        top_expense = None
        if month_expenses:
            top_exp_obj = max(month_expenses, key=lambda x: float(x.get("amount", 0.0)))
            top_expense = {
                "id": top_exp_obj.get("id"),
                "description": top_exp_obj.get("description", "Untitled"),
                "category": top_exp_obj.get("category"),
                "amount": float(top_exp_obj.get("amount", 0.0)),
                "formatted": format_inr(float(top_exp_obj.get("amount", 0.0)))
            }

        is_over_budget = total_month > monthly_budget
        remaining_budget = max(0.0, monthly_budget - total_month)
        over_budget_amount = max(0.0, total_month - monthly_budget)
        budget_percent = (total_month / monthly_budget * 100) if monthly_budget > 0 else 0.0

        months_set = set()
        for e in expenses:
            d = str(e.get("date", ""))
            if len(d) >= 7:
                months_set.add(d[:7])
        if current_month != "all" and current_month not in months_set:
            months_set.add(current_month)
        available_months = sorted(list(months_set), reverse=True)

        return {
            "selected_month": current_month,
            "month_display_name": month_display,
            "total_expenses_month": total_month,
            "total_expenses_month_formatted": format_inr(total_month),
            "total_expenses_all_time": total_all_time,
            "total_expenses_all_time_formatted": format_inr(total_all_time),
            "monthly_budget": monthly_budget,
            "monthly_budget_formatted": format_inr(monthly_budget),
            "remaining_budget": remaining_budget,
            "remaining_budget_formatted": format_inr(remaining_budget),
            "over_budget_amount": over_budget_amount,
            "over_budget_amount_formatted": format_inr(over_budget_amount),
            "is_over_budget": is_over_budget,
            "budget_usage_percentage": min(100.0, round(budget_percent, 1)),
            "budget_real_percentage": round(budget_percent, 1),
            "top_category": top_category,
            "top_category_amount": top_category_amount,
            "top_category_amount_formatted": format_inr(top_category_amount),
            "top_expense": top_expense,
            "category_breakdown": sorted_categories,
            "payment_breakdown": sorted_payments,
            "status_counts": status_counts,
            "status_totals": {k: format_inr(v) for k, v in status_totals.items()},
            "total_transactions_count": len(month_expenses),
            "all_transactions_count": len(expenses),
            "available_months": available_months
        }

    def export_to_csv(self) -> str:
        """Export expenses to CSV string."""
        expenses = self.load_expenses()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Expense ID", "Date", "Category", "Description", "Amount", "Payment Method", "Status", "Created At"])
        
        for exp in expenses:
            writer.writerow([
                exp.get("id", ""),
                exp.get("date", ""),
                exp.get("category", ""),
                exp.get("description", ""),
                exp.get("amount", 0.0),
                exp.get("payment_method", ""),
                exp.get("status", ""),
                exp.get("created_at", "")
            ])
            
        return output.getvalue()

    def import_from_csv(self, csv_content: str, overwrite: bool = False) -> int:
        """Import expenses from CSV string. Returns count of imported items."""
        reader = csv.reader(io.StringIO(csv_content))
        rows = list(reader)
        if not rows:
            return 0

        header = [h.strip().lower() for h in rows[0]]
        
        id_idx = next((i for i, h in enumerate(header) if "id" in h), 0)
        date_idx = next((i for i, h in enumerate(header) if "date" in h), 1)
        cat_idx = next((i for i, h in enumerate(header) if "category" in h), 2)
        desc_idx = next((i for i, h in enumerate(header) if "desc" in h), 3)
        amount_idx = next((i for i, h in enumerate(header) if "amount" in h), 4)
        payment_idx = next((i for i, h in enumerate(header) if "payment" in h or "method" in h), 5)
        status_idx = next((i for i, h in enumerate(header) if "status" in h), 6)

        existing = [] if overwrite else self.load_expenses()
        existing_ids = {str(e.get("id")).strip() for e in existing}
        imported_count = 0

        for row in rows[1:]:
            if not row or all(c.strip() == "" for c in row):
                continue
            
            exp_id = row[id_idx].strip() if len(row) > id_idx else ""
            date_val = row[date_idx].strip() if len(row) > date_idx else datetime.now().strftime("%Y-%m-%d")
            category_val = row[cat_idx].strip() if len(row) > cat_idx else "Miscellaneous"
            description_val = row[desc_idx].strip() if len(row) > desc_idx else ""
            
            try:
                raw_amt = row[amount_idx].replace("₹", "").replace(",", "").strip() if len(row) > amount_idx else "0"
                amount_val = float(raw_amt)
            except Exception:
                amount_val = 0.0

            payment_val = row[payment_idx].strip() if len(row) > payment_idx else "Cash"
            status_val = row[status_idx].strip() if len(row) > status_idx else "Paid"

            if not exp_id or exp_id in existing_ids:
                exp_id = self.generate_next_id()

            item = {
                "id": exp_id,
                "date": date_val,
                "category": category_val,
                "description": description_val,
                "amount": amount_val,
                "payment_method": payment_val,
                "status": status_val,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            existing.append(item)
            existing_ids.add(exp_id)
            imported_count += 1

        self.save_expenses(existing)
        return imported_count

    def generate_text_report(self, month: Optional[str] = None) -> str:
        """Generate formatted executive ASCII Business Expense Report matching user spec."""
        summary = self.get_summary_metrics(month)
        
        top_exp_str = f"{summary['top_expense']['description']} — {summary['top_expense']['formatted']}" if summary['top_expense'] else "None"
        top_cat_str = f"{summary['top_category']} — {summary['top_category_amount_formatted']}"

        lines = [
            "===========================================================",
            "                  BUSINESS EXPENSE REPORT                  ",
            f"                  Period: {summary['month_display_name']}   ",
            "===========================================================",
            f"Total Expenses       : {summary['total_expenses_month_formatted']}",
            f"Monthly Budget       : {summary['monthly_budget_formatted']}",
        ]

        if summary['is_over_budget']:
            lines.append(f"⚠ Budget Exceeded!   : Over by {summary['over_budget_amount_formatted']} ({summary['budget_real_percentage']}% used)")
        else:
            lines.append(f"Remaining Budget     : {summary['remaining_budget_formatted']} ({100 - summary['budget_real_percentage']:.1f}% remaining)")

        lines.extend([
            "",
            f"Top Category         : {top_cat_str}",
            f"Top Expense          : {top_exp_str}",
            "",
            "Payment Breakdown:",
        ])

        for p in summary['payment_breakdown']:
            lines.append(f"  {p['method']:<18} : {p['formatted']:<12} ({p['percentage']:.1f}%)")

        lines.extend([
            "",
            "Category Breakdown:",
        ])

        for c in summary['category_breakdown']:
            lines.append(f"  {c['category']:<22} : {c['formatted']:<12} ({c['percentage']:.1f}%)")

        lines.extend([
            "==========================================================="
        ])

        return "\n".join(lines)
