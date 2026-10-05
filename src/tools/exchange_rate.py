def get_exchange_rate(
        from_currency: str,
        to_currency: str
    ) -> float:

    mock_rates = {
        ("USD", "INR"): 92.0,
        ("EUR", "INR"): 107.0,
        ("USD", "EUR"): 0.86,
    }

    key = (
        from_currency.upper(),
        to_currency.upper()
    )

    if key not in mock_rates:
        raise ValueError(
            f"Exchange rate not available for "
            f"{from_currency} -> {to_currency}"
        )

    return mock_rates[key]