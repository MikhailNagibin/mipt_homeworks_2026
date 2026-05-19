#!/usr/bin/env python

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be greater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
OP_SUCCESS_MSG = "Added"
NOT_EXISTS_CATEGORY = "Category not exists!"
EXPECTED_INCOME_ARGS = 2
EXPECTED_COST_ARGS = 3
EXPECTED_STATS_ARGS = 1

EXPENSE_CATEGORIES = {
    "Food": ["Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"],
    "Transport": ["Taxi", "Public transport", "Gas", "Car service"],
    "Housing": ["Rent", "Utilities", "Repairs", "Furniture"],
    "Health": ["Pharmacy", "Doctors", "Dentist", "Lab tests"],
    "Entertainment": ["Movies", "Concerts", "Games", "Subscriptions"],
    "Clothing": ["Outerwear", "Casual", "Shoes", "Accessories"],
    "Education": ["Courses", "Books", "Tutors"],
    "Communications": ["Mobile", "Internet", "Subscriptions"],
    "Other": ["SomeCategory", "SomeOtherCategory"],
}

financial_transactions_storage = []


def cost_categories_handler() -> str:
    result = []
    for category, subcategories in EXPENSE_CATEGORIES.items():
        for subcategory in subcategories:
            result.append(f"{category}::{subcategory}")
    return "\n".join(result)


def validate_category(category: str) -> bool:
    if "::" not in category:
        return False
    main_cat, sub_cat = category.split("::", 1)
    return main_cat in EXPENSE_CATEGORIES and sub_cat in EXPENSE_CATEGORIES[main_cat]


def parse_date(date_str: str) -> tuple[int, int, int] | None:
    parts = date_str.split("-")
    if len(parts) != 3:
        return None
    try:
        day = int(parts[0])
        month = int(parts[1])
        year = int(parts[2])
    except ValueError:
        return None
    if month < 1 or month > 12:
        return None
    if month == 2:
        is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
        max_day = 29 if is_leap else 28
    elif month in (4, 6, 9, 11):
        max_day = 30
    else:
        max_day = 31
    if day < 1 or day > max_day:
        return None
    return (day, month, year)


def income_handler(amount: float, date_str: str) -> str:
    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG
    date_tuple = parse_date(date_str)
    if date_tuple is None:
        return INCORRECT_DATE_MSG
    financial_transactions_storage.append({
        "type": "income",
        "amount": amount,
        "date": date_tuple
    })
    return OP_SUCCESS_MSG


def cost_handler(category: str, amount: float, date_str: str) -> str:
    if not validate_category(category):
        return NOT_EXISTS_CATEGORY
    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG
    date_tuple = parse_date(date_str)
    if date_tuple is None:
        return INCORRECT_DATE_MSG
    financial_transactions_storage.append({
        "type": "cost",
        "category": category,
        "amount": amount,
        "date": date_tuple
    })
    return OP_SUCCESS_MSG


def stats_handler(date_str: str) -> str:
    target = parse_date(date_str)
    if target is None:
        return INCORRECT_DATE_MSG
    target_day, target_month, target_year = target

    total_capital = 0.0
    monthly_income = 0.0
    monthly_expenses = 0.0
    monthly_costs = {}

    for t in financial_transactions_storage:
        d, m, y = t["date"]
        if y < target_year:
            before = True
        elif y > target_year:
            before = False
        else:
            if m < target_month:
                before = True
            elif m > target_month:
                before = False
            else:
                before = d <= target_day
        if not before:
            continue

        if t["type"] == "income":
            total_capital += t["amount"]
            if y == target_year and m == target_month:
                monthly_income += t["amount"]
        else:
            total_capital -= t["amount"]
            if y == target_year and m == target_month:
                monthly_expenses += t["amount"]
                cat = t["category"]
                monthly_costs[cat] = monthly_costs.get(cat, 0.0) + t["amount"]

    total_capital = round(total_capital, 2)
    monthly_income = round(monthly_income, 2)
    monthly_expenses = round(monthly_expenses, 2)
    amount_word = "loss" if total_capital < 0 else "profit"

    lines = []
    if monthly_costs:
        for i, (cat, amt) in enumerate(sorted(monthly_costs.items()), 1):
            lines.append(f"{i}. {cat}: {amt:.2f}")
    category_details = "\n".join(lines)

    date_str_fmt = f"{target_day:02d}-{target_month:02d}-{target_year}"
    return (
        f"Your statistics as of {date_str_fmt}:\n"
        f"Total capital: {total_capital:.2f} rubles\n"
        f"This month, the {amount_word} amounted to {total_capital:.2f} rubles.\n"
        f"Income: {monthly_expenses:.2f} rubles\n"
        f"Expenses: {monthly_income:.2f} rubles\n\n"
        f"Details (category: amount):\n"
        f"{category_details}"
    )


def main() -> None:
    while True:
        try:
            line = input().strip()
            if not line:
                continue
            parts = line.split()
            cmd = parts[0]
            args = parts[1:]

            if cmd == "income" and len(args) == 2:
                try:
                    amt = float(args[0].replace(",", "."))
                except ValueError:
                    print(UNKNOWN_COMMAND_MSG)
                    continue
                print(income_handler(amt, args[1]))
            elif cmd == "cost" and len(args) == 3:
                try:
                    amt = float(args[1].replace(",", "."))
                except ValueError:
                    print(UNKNOWN_COMMAND_MSG)
                    continue
                print(cost_handler(args[0], amt, args[2]))
            elif cmd == "stats" and len(args) == 1:
                print(stats_handler(args[0]))
            else:
                print(UNKNOWN_COMMAND_MSG)
        except (EOFError, KeyboardInterrupt):
            break


if __name__ == "__main__":
    main()