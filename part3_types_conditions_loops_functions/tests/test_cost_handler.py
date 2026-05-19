from part3_types_conditions_loops_functions import hw3
from part3_types_conditions_loops_functions.tests.conftest import Cost, CostBuilder, parse_date


def test_cost_success(valid_cost: Cost) -> None:
    result = hw3.cost_handler(valid_cost.category, valid_cost.amount, valid_cost.date)
    cost_data = hw3.financial_transactions_storage[-1]
    assert result == hw3.OP_SUCCESS_MSG  # noqa: S101
    assert cost_data  # noqa: S101
    assert cost_data["amount"] == valid_cost.amount  # noqa: S101
    assert cost_data["date"] == parse_date(valid_cost.date)  # noqa: S101
    common_category, direct_category = valid_cost.category.split("::")
    assert common_category in hw3.EXPENSE_CATEGORIES  # noqa: S101
    assert direct_category in hw3.EXPENSE_CATEGORIES[common_category]  # noqa: S101


def test_cost_amount_less_than_zero(invalid_cost_factory: CostBuilder[Cost]) -> None:
    invalid_income = invalid_cost_factory(amount=-1)
    result = hw3.cost_handler(invalid_income.category, invalid_income.amount, invalid_income.date)
    income_data = hw3.financial_transactions_storage[-1]
    assert result == hw3.NONPOSITIVE_VALUE_MSG  # noqa: S101
    assert not income_data  # noqa: S101


def test_cost_invalid_date(invalid_cost_factory: CostBuilder[Cost]) -> None:
    invalid_income = invalid_cost_factory(date="invalid")
    result = hw3.cost_handler(invalid_income.category, invalid_income.amount, invalid_income.date)
    income_data = hw3.financial_transactions_storage[-1]
    assert result == hw3.INCORRECT_DATE_MSG  # noqa: S101
    assert not income_data  # noqa: S101


def test_cost_invalid_category(invalid_cost_factory: CostBuilder[Cost]) -> None:
    invalid_income = invalid_cost_factory(category="NotExistCategory")
    result = hw3.cost_handler(invalid_income.category, invalid_income.amount, invalid_income.date)
    income_data = hw3.financial_transactions_storage[-1]
    assert result == hw3.NOT_EXISTS_CATEGORY  # noqa: S101
    assert not income_data  # noqa: S101


def test_cost_categories_info() -> None:
    result = hw3.cost_categories_handler()
    expected = "\n".join(f"{k}::{v}" for k, kv in hw3.EXPENSE_CATEGORIES.items() for v in kv)
    assert result == expected  # noqa: S101
