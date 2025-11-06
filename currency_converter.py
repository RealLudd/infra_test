"""
Currency Converter for PACO/FRAN Data
Converts all amounts to EUR for consistent reporting
Exchange rates updated as of November 5, 2025
"""

# Exchange rates to EUR (1 unit = X EUR)
# Update these rates as needed
EXCHANGE_RATES = {
    'EUR': 1.0,              # Base currency
    'USD': 0.92,             # US Dollar
    'GBP': 1.17,             # British Pound
    'GBP2': 1.17,            # British Pound (variant naming)
    'CHF': 1.05,             # Swiss Franc
    'PLN': 0.23,             # Polish Zloty
    'CZK': 0.039,            # Czech Koruna
    'NOK': 0.084,            # Norwegian Krone
    'NOK_2': 0.084,          # Norwegian Krone (variant naming)
    'SEK': 0.084,            # Swedish Krona
    
    # Special account codes (assumed EUR-based)
    'OP272': 1.0,            # Operational account (EUR)
    'OP464': 1.0,            # Operational account (EUR)
}

def convert_to_eur(amount, currency):
    """
    Convert amount from given currency to EUR
    
    Args:
        amount (float): Amount in original currency
        currency (str): Currency code (e.g., 'USD', 'GBP', 'EUR')
    
    Returns:
        float: Amount converted to EUR
    """
    if amount is None or amount == 0:
        return 0.0
    
    # Normalize currency code
    currency_upper = str(currency).strip().upper()
    
    # Get exchange rate
    rate = EXCHANGE_RATES.get(currency_upper, None)
    
    if rate is None:
        print(f"Warning: Unknown currency '{currency}', assuming EUR (1.0)")
        rate = 1.0
    
    return float(amount) * rate

def get_exchange_rate(currency):
    """
    Get exchange rate for a currency to EUR
    
    Args:
        currency (str): Currency code
    
    Returns:
        float: Exchange rate (1 unit = X EUR)
    """
    currency_upper = str(currency).strip().upper()
    return EXCHANGE_RATES.get(currency_upper, 1.0)

def format_amount_eur(amount):
    """
    Format EUR amount for display
    
    Args:
        amount (float): Amount in EUR
    
    Returns:
        str: Formatted string (e.g., "€1,234.56")
    """
    return f"€{amount:,.2f}"

def update_rates_from_api():
    """
    Placeholder for future API integration to fetch live rates
    Could integrate with ECB, exchangerate-api, or similar
    """
    # TODO: Implement API integration if needed
    pass

if __name__ == '__main__':
    # Test conversions
    print("Currency Conversion Tests:")
    print("-" * 50)
    
    test_cases = [
        (1000, 'USD'),
        (1000, 'GBP2'),
        (1000, 'CHF'),
        (1000, 'PLN'),
        (1000, 'CZK'),
        (1000, 'NOK'),
        (1000, 'EUR'),
        (1000, 'OP272'),
    ]
    
    for amount, currency in test_cases:
        eur_amount = convert_to_eur(amount, currency)
        rate = get_exchange_rate(currency)
        print(f"{amount:>8,.0f} {currency:<6} = {format_amount_eur(eur_amount)} (rate: {rate})")

