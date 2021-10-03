from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import backtrader as bt
import datetime
import os
import sys
import pandas as pd
from backtrader import plot
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import yfinance as yf
# Import the backtrader platform
import backtrader as bt
from Strategies import MAcrossover, BuyAndHold_1, BuyAfterBigRed
from tabulate import tabulate
from analyzers import TradeList
from dataframe import analyze_data

if __name__ == '__main__':

    Tickers = ['VOO', 'AAPL', 'TSLA', 'MSFT', 'GOOGL', 'NFLX', 'HD', 'FB', 'XOM', 'C', 'BAC', 'INTU', 'GS', 'TWTR', 'WMT', 'IAU', 'TTD', 'CVS', 'IRBT', 'DIS']
    Start_Date = '2018-01-01'
    End_Date = '2021-09-26'

    lines = []
    for Ticker in Tickers:
        # Create a cerebro entity
        cerebro = bt.Cerebro()

        print(Ticker)
        # Create a data feed
        data = bt.feeds.PandasData(dataname=yf.download(Ticker, Start_Date, End_Date, auto_adjust=True))
        #data = bt.feeds.YahooFinanceData(dataname=Ticker, fromdate=datetime.datetime(2018, 1, 1),
        #                                 todate=datetime.datetime(2021, 9, 26))
        # Add the Data Feed to Cerebro
        cerebro.adddata(data, name=Ticker)
        # Add a strategy
        # cerebro.addstrategy(MAcrossover, fast=20, slow=50)

        cerebro.addstrategy(BuyAfterBigRed, pctdrop=-3, days_to_hold=0)
        # cerebro.addstrategy(BuyAndHold_1)

        # Set our desired cash start
        cerebro.broker.setcash(10000.0)
        # Add a FixedSize sizer according to the stake
        #cerebro.addsizer(bt.sizers.FixedSize, stake=10)
        # Set the commission
        cerebro.broker.setcommission(commission=0.001)
        # Print out the starting conditions
        starting_portfolio_value = float(cerebro.broker.getvalue())
        print('Starting Portfolio Value: %.2f' % starting_portfolio_value)
        # Run over everything
        # cerebro.run()
        # Print out the final result
        # add analyzers
        cerebro.addanalyzer(TradeList, _name='trade_list')
        # run backtest
        strats = cerebro.run(tradehistory=True)
        # get analyzers data
        trade_list = strats[0].analyzers.trade_list.get_analysis()
        output = tabulate(trade_list, headers="keys")
        df = pd.DataFrame(trade_list)
        lines.append(analyze_data(df, ticker=Ticker, starting_cash=starting_portfolio_value,
                                  start_date=Start_Date, end_date=End_Date))
        df.to_excel('Completed Analysis/{}_{}_{}.xlsx'.format(Ticker, Start_Date, End_Date))
        #print(output)
        text_file = open("output.csv", "w")
        text_file.write(output)
        text_file.close()

        ending_portfolio_value = float(cerebro.broker.getvalue())
        profit = ending_portfolio_value-starting_portfolio_value
        print('Final Portfolio Value: %.2f' % ending_portfolio_value)
        print('Profit: %.2f' % profit)
        roi = 100*profit/starting_portfolio_value
        print('ROI: %.2f' % roi + '%')
        #print('ROI: %.2f' % (ending_portfolio_value-starting_portfolio_value)/starting_portfolio_value)
    # Plot the result
    # cerebro.plot()
    df_all = pd.DataFrame(lines, columns=['Ticker', 'Starting Cash', 'Ending Cash',
                                          'Count of Trades', 'Count of Winning Trades',
                                          'Winning %', 'Avg P/L', 'Total P/L', 'ROI',
                                          'Analysis Start Date', 'Analysis End Date'])
    df_all.to_excel('Completed Analysis/Summary.xlsx')
