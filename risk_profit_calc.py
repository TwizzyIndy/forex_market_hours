def calculate_risk_and_profit(trading_capital, daily_profit_percent, daily_risk_percent, position_size_percent):
    position_size_per_trade = (trading_capital * position_size_percent) / 100
    maximum_risk_per_trade = (trading_capital * daily_risk_percent) / 100
    maximum_risk_percentage_per_trade = (maximum_risk_per_trade / position_size_per_trade) * 100

    min_possible_daily_profit = (position_size_per_trade * daily_profit_percent) / 100
    max_possible_daily_profit = (trading_capital * daily_profit_percent) / 100

    min_possible_daily_loss = (position_size_per_trade * daily_risk_percent) / 100
    max_possible_daily_loss = (trading_capital * daily_risk_percent) / 100

    min_possible_monthly_profit = min_possible_daily_profit * 20
    max_possible_monthly_profit = max_possible_daily_profit * 20

    min_possible_monthly_loss = min_possible_daily_loss * 20
    max_possible_monthly_loss = max_possible_daily_loss * 20

    min_possible_yearly_profit = min_possible_monthly_profit * 12
    max_possible_yearly_profit = max_possible_monthly_profit * 12

    min_possible_yearly_loss = min_possible_monthly_loss * 12
    max_possible_yearly_loss = max_possible_monthly_loss * 12

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

def main():
    tradingCapital = float(input("Enter your trading capital: "))
    maximumDailyProfitTargetPercentage = float(input("Enter your maximum daily profit target %: "))
    maximumDailyRiskPercent = float(input("Enter your maximum daily risk %: "))
    positionSizePercentPerTrade = float(input("Enter your position size per trade %: "))

    print('')

    results = calculate_risk_and_profit(
        tradingCapital,
        maximumDailyProfitTargetPercentage,
        maximumDailyRiskPercent,
        positionSizePercentPerTrade
    )

    print(f"Position size per trade: {results['position_size_per_trade']} $")
    print(f"Daily Maximum Risk per trade: {results['maximum_risk_per_trade']} $")
    print(f"Daily Maximum Risk per trade %: {results['maximum_risk_percentage_per_trade']} %\n")

    print(f"Possible daily profit: {results['min_daily_profit']} ~ {results['max_daily_profit']} $")
    print(f"Possible daily loss: {results['min_daily_loss']} ~ {results['max_daily_loss']} $")
    print(f"Possible monthly profit: {results['min_monthly_profit']} ~ {results['max_monthly_profit']} $")
    print(f"Possible monthly loss: {results['min_monthly_loss']} ~ {results['max_monthly_loss']} $")
    print(f"Possible yearly profit: {results['min_yearly_profit']} ~ {results['max_yearly_profit']} $")
    print(f"Possible yearly loss: {results['min_yearly_loss']} ~ {results['max_yearly_loss']} $")

if __name__ == '__main__':
    main()
