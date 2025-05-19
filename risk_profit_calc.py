def calculate_risk_and_profit(trading_capital, daily_profit_percent, daily_risk_percent, position_size_percent):
    """
    Calculate risk and profit metrics for trading.
    Args:
        trading_capital (float): Total trading capital.
        daily_profit_percent (float): Daily profit target as a percentage.
        daily_risk_percent (float): Daily risk as a percentage.
        position_size_percent (float): Position size per trade as a percentage.
    Returns:
        dict: Calculated risk and profit values.
    """
    # Constants for trading days and months
    TRADING_DAYS_PER_MONTH = 20
    MONTHS_PER_YEAR = 12

    position_size_per_trade = (trading_capital * position_size_percent) / 100
    maximum_risk_per_trade = (trading_capital * daily_risk_percent) / 100
    maximum_risk_percentage_per_trade = (maximum_risk_per_trade / position_size_per_trade) * 100 if position_size_per_trade != 0 else 0

    min_possible_daily_profit = (position_size_per_trade * daily_profit_percent) / 100
    max_possible_daily_profit = (trading_capital * daily_profit_percent) / 100

    min_possible_daily_loss = (position_size_per_trade * daily_risk_percent) / 100
    max_possible_daily_loss = (trading_capital * daily_risk_percent) / 100

    min_possible_monthly_profit = min_possible_daily_profit * TRADING_DAYS_PER_MONTH
    max_possible_monthly_profit = max_possible_daily_profit * TRADING_DAYS_PER_MONTH

    min_possible_monthly_loss = min_possible_daily_loss * TRADING_DAYS_PER_MONTH
    max_possible_monthly_loss = max_possible_daily_loss * TRADING_DAYS_PER_MONTH

    min_possible_yearly_profit = min_possible_monthly_profit * MONTHS_PER_YEAR
    max_possible_yearly_profit = max_possible_monthly_profit * MONTHS_PER_YEAR

    min_possible_yearly_loss = min_possible_monthly_loss * MONTHS_PER_YEAR
    max_possible_yearly_loss = max_possible_monthly_loss * MONTHS_PER_YEAR

    return {
        "position_size_per_trade": position_size_per_trade,
        "maximum_risk_per_trade": maximum_risk_per_trade,
        "maximum_risk_percentage_per_trade": maximum_risk_percentage_per_trade,
        "min_daily_profit": min_possible_daily_profit,
        "max_daily_profit": max_possible_daily_profit,
        "min_daily_loss": min_possible_daily_loss,
        "max_daily_loss": max_possible_daily_loss,
        "min_monthly_profit": min_possible_monthly_profit,
        "max_monthly_profit": max_possible_monthly_profit,
        "min_monthly_loss": min_possible_monthly_loss,
        "max_monthly_loss": max_possible_monthly_loss,
        "min_yearly_profit": min_possible_yearly_profit,
        "max_yearly_profit": max_possible_yearly_profit,
        "min_yearly_loss": min_possible_yearly_loss,
        "max_yearly_loss": max_possible_yearly_loss
    }

def calculate_required_capital(expected_profit, daily_profit_percent, position_size_percent):
    """
    Calculate the required trading capital to achieve a specific profit target,
    assuming the daily_profit_percent is achieved on the specified position_size_percent of the capital.

    Args:
        expected_profit (float): The user's expected profit amount (per day).
        daily_profit_percent (float): Daily profit target as a percentage of the position size.
        position_size_percent (float): Position size per trade as a percentage of total capital.

    Returns:
        float or None: Required trading capital, or None if inputs are invalid (e.g., non-positive percentages).
    """
    if daily_profit_percent > 0 and position_size_percent > 0:
        # Convert percentages to decimals
        profit_rate_on_position = daily_profit_percent / 100.0
        position_size_as_fraction_of_capital = position_size_percent / 100.0
        
        # Formula derivation:
        # expected_profit = (required_capital * position_size_as_fraction_of_capital) * profit_rate_on_position
        # So, required_capital = expected_profit / (position_size_as_fraction_of_capital * profit_rate_on_position)
        required_capital = expected_profit / (position_size_as_fraction_of_capital * profit_rate_on_position)
        return required_capital
    else:
        # Cannot calculate if profit percent or position size percent is not positive
        return None

def get_float_input(prompt, min_value=0.0, max_value=None):
    """
    Prompt the user for a float input with validation.
    """
    while True:
        try:
            value = float(input(prompt))
            if value < min_value or (max_value is not None and value > max_value):
                print(f"Value must be >= {min_value}" + (f" and <= {max_value}" if max_value is not None else ""))
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a number.")


def main():
    print("--- Forex Risk & Profit Calculator ---\n")
    print("1. Calculate risk and profit based on your capital")
    print("2. Calculate required capital for your profit target")
    choice = input("Choose an option (1 or 2): ").strip()
    print("")

    if choice == '1':
        tradingCapital = get_float_input("Enter your trading capital: ", min_value=0.01)
        maximumDailyProfitTargetPercentage = get_float_input("Enter your maximum daily profit target %: ", min_value=0.01, max_value=100)
        maximumDailyRiskPercent = get_float_input("Enter your maximum daily risk %: ", min_value=0.01, max_value=100)
        positionSizePercentPerTrade = get_float_input("Enter your position size per trade %: ", min_value=0.01, max_value=100)

        print('')

        results = calculate_risk_and_profit(
            tradingCapital,
            maximumDailyProfitTargetPercentage,
            maximumDailyRiskPercent,
            positionSizePercentPerTrade
        )

        print(f"Position size per trade: {results['position_size_per_trade']:.2f} $")
        print(f"Daily Maximum Risk per trade: {results['maximum_risk_per_trade']:.2f} $")
        print(f"Daily Maximum Risk per trade %: {results['maximum_risk_percentage_per_trade']:.2f} %\n")

        print(f"Possible daily profit: {results['min_daily_profit']:.2f} ~ {results['max_daily_profit']:.2f} $")
        print(f"Possible daily loss: {results['min_daily_loss']:.2f} ~ {results['max_daily_loss']:.2f} $")
        print(f"Possible monthly profit: {results['min_monthly_profit']:.2f} ~ {results['max_monthly_profit']:.2f} $")
        print(f"Possible monthly loss: {results['min_monthly_loss']:.2f} ~ {results['max_monthly_loss']:.2f} $")
        print(f"Possible yearly profit: {results['min_yearly_profit']:.2f} ~ {results['max_yearly_profit']:.2f} $")
        print(f"Possible yearly loss: {results['min_yearly_loss']:.2f} ~ {results['max_yearly_loss']:.2f} $")
    elif choice == '2':
        expectedProfit = get_float_input("Enter your expected daily profit target ($): ", min_value=0.01)
        dailyProfitPercent = get_float_input("Enter your daily profit target %: ", min_value=0.01, max_value=100)
        positionSizePercent = get_float_input("Enter your position size per trade %: ", min_value=0.01, max_value=100)
        requiredCapital = calculate_required_capital(expectedProfit, dailyProfitPercent, positionSizePercent)
        if requiredCapital is not None:
            print(f"\nYou need at least: {requiredCapital:.2f} $ trading capital to reach a daily profit of {expectedProfit:.2f} $ with a {dailyProfitPercent:.2f}% target.")
        else:
            print("\nInvalid input. Cannot calculate required capital.")
    else:
        print("Invalid option. Please run the program again.")

if __name__ == '__main__':
    main()
