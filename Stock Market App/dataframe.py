import pandas as pd


def analyze_data(df, ticker, starting_cash, start_date, end_date):
    number_of_trades = len(df)
    winning_trades = len(df[df['pnl']>0])
    winning_pct = 100*winning_trades/number_of_trades
    avg_pnl_pct = df['pnl%'].mean()
    total_profit_loss = df['cumpnl'].values[-1]
    roi = 100*total_profit_loss/starting_cash
    ending_cash = starting_cash + total_profit_loss
    return [ticker, starting_cash, ending_cash, number_of_trades, winning_trades,
            winning_pct, avg_pnl_pct, total_profit_loss, roi, start_date, end_date]
