import os
from models import ExpenseManager

SAMPLE_EXPENSES = [
    {
        "id": "101",
        "date": "2026-08-03",
        "category": "Travel",
        "description": "Client Meeting Travel & Cab Fare",
        "amount": 5000.0,
        "payment_method": "UPI",
        "status": "Paid"
    },
    {
        "id": "102",
        "date": "2026-08-05",
        "category": "Marketing",
        "description": "Marketing Campaign - Meta & Google Ads",
        "amount": 18000.0,
        "payment_method": "UPI",
        "status": "Paid"
    },
    {
        "id": "103",
        "date": "2026-08-08",
        "category": "Office Supplies",
        "description": "Printer Cartridges, Paper & Stationery",
        "amount": 8200.0,
        "payment_method": "Credit/Debit Card",
        "status": "Reimbursed"
    },
    {
        "id": "104",
        "date": "2026-08-01",
        "category": "Rent",
        "description": "August Main Office Space Rent",
        "amount": 40000.0,
        "payment_method": "Bank Transfer",
        "status": "Paid"
    },
    {
        "id": "105",
        "date": "2026-08-12",
        "category": "Marketing",
        "description": "Influencer Brand Collaboration & PR",
        "amount": 7000.0,
        "payment_method": "UPI",
        "status": "Paid"
    },
    {
        "id": "106",
        "date": "2026-08-14",
        "category": "Transportation",
        "description": "Logistics, Delivery & Warehouse Courier",
        "amount": 12500.0,
        "payment_method": "Cash",
        "status": "Paid"
    },
    {
        "id": "107",
        "date": "2026-08-15",
        "category": "Electricity",
        "description": "Commercial Electricity & Utility Bill",
        "amount": 9500.0,
        "payment_method": "Bank Transfer",
        "status": "Paid"
    },
    {
        "id": "108",
        "date": "2026-08-18",
        "category": "Software/Subscriptions",
        "description": "AWS Cloud Hosting, GitHub & Figma Subscriptions",
        "amount": 12000.0,
        "payment_method": "Credit/Debit Card",
        "status": "Paid"
    },
    {
        "id": "109",
        "date": "2026-08-20",
        "category": "Equipment",
        "description": "Ergonomic Chairs for Design Team",
        "amount": 10300.0,
        "payment_method": "Credit/Debit Card",
        "status": "Paid"
    },
    {
        "id": "110",
        "date": "2026-08-22",
        "category": "Miscellaneous",
        "description": "Team Refreshments & Client Lunch",
        "amount": 2000.0,
        "payment_method": "Cash",
        "status": "Pending"
    },
    {
        "id": "111",
        "date": "2026-07-28",
        "category": "Office Supplies",
        "description": "Desk Organizers & Whiteboards",
        "amount": 4500.0,
        "payment_method": "Credit/Debit Card",
        "status": "Paid"
    },
    {
        "id": "112",
        "date": "2026-07-15",
        "category": "Salaries",
        "description": "Freelance UI/UX Contractor Stipend",
        "amount": 25000.0,
        "payment_method": "Bank Transfer",
        "status": "Paid"
    }
]

def seed_sample_data(data_dir: str):
    manager = ExpenseManager(data_dir)
    existing = manager.load_expenses()
    if not existing:
        for item in SAMPLE_EXPENSES:
            manager.add_expense(item)
        print("Sample data populated successfully!")
    else:
        print("Data already exists. Skipping auto-seed.")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "data")
    seed_sample_data(data_dir)
