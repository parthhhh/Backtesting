import backtrader as bt
import pandas as pd


class BuyAfterBigRed(bt.Strategy):

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s %s' % (dt.isoformat(), txt))

    def __init__(self, pctdrop, days_to_hold):
        self.pctdrop = pctdrop
        self.dataclose = self.datas[0].close
        self.dataopen = self.datas[0].open
        self.drop = 100*(self.dataclose - self.dataopen) / self.dataopen
        self.days_to_hold = days_to_hold
        self.output = []

        # Order variable will contain ongoing order details/status
        self.order = None

    def notify_order(self, order):
        if order.status in [order.Submitted or order.Accepted]:
            # Take no action if order has already been submitted or accepted
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, Price: {}, Cost: {}, Size: {}'.format(order.executed.price,
                                                                              order.executed.price*self.size, self.size))
                self.output.append(['BUY EXECUTED', self.datas[0].datetime.date(0), order.executed.price, self.size])
            elif order.issell():
                self.log('SELL EXECUTED Price: {}, Cost: {}, Size: {}'.format(order.executed.price,
                                                                              order.executed.price*self.size, self.size))
                self.output.append(['BUY EXECUTED', self.datas[0].datetime.date(0), order.executed.price, self.size])
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Reset order
        self.order = None

    def next(self):
        # Check if we are in a position
        if self.order:
            return

        # Check if we are in a position
        if not self.position:
            # We are not in a position
            if self.drop < self.pctdrop:
                # Drop in the daily candle is more than we specified
                self.log('BUY CREATE: {}'.format(self.dataclose[0]))
                # Specify the size of the order - we will go all in
                self.size = int(self.broker.get_cash()/self.data)
                # We will buy on the next opening day
                self.order = self.buy(size=self.size)
        else:
            # We are in a position, lets sell on the next day
            if len(self) >= (self.bar_executed + self.days_to_hold):
                self.order = self.sell(size=self.size)
                self.log('SELL CREATE: {}'.format(self.dataclose[0]))

 #   def output_csv(self):
 #       df = pd.DataFrame(self.output, columns=['Description', 'Date', 'Price', 'Size'])
 #       return df





class MAcrossover(bt.Strategy):
    # Moving average parameters
    #params = (('pfast', 20), ('pslow', 50),)

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self, fast, slow):
        self.dataclose = self.datas[0].close
        self.fast = fast
        self.slow = slow

        # Order variable will contain ongoing order details/status
        self.order = None

        # Instantiate moving averages
        self.slow_sma = bt.indicators.MovingAverageSimple(self.datas[0],
                                                          period=self.slow)
        self.fast_sma = bt.indicators.MovingAverageSimple(self.datas[0],
                                                          period=self.fast)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # An active Buy/Sell order has been submitted/accepted - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, Price: {}, Cost: {}, Size: {}'.format(order.executed.price,
                                                                              order.executed.price*self.size, self.size))
            elif order.issell():
                self.log('SELL EXECUTED Price: {}, Cost: {}, Size: {}'.format(order.executed.price,
                                                                              order.executed.price*self.size, self.size))
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Reset orders
        self.order = None

    def next(self):
        # Check for open orders
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            # We are not in the market, look for a signal to OPEN trades

            # If the 20 SMA is above the 50 SMA
            if self.fast_sma[0] > self.slow_sma[0] and self.fast_sma[-1] < self.slow_sma[-1]:
                self.log('BUY CREATE {}'.format(self.dataclose[0]))
                # Keep track of the created order to avoid a 2nd order

                self.size = int(self.broker.get_cash() / self.data)
                self.order = self.buy(size=self.size)
                self.buying_price = self.dataclose[0]
            # Otherwise if the 20 SMA is below the 50 SMA
            # elif self.fast_sma[0] < self.slow_sma[0] and self.fast_sma[-1] > self.slow_sma[-1]:
            #     self.log('SELL CREATE {}'.format(self.dataclose[0]))
            #     # Keep track of the created order to avoid a 2nd order
            #     self.order = self.sell()
        else:
            if self.fast_sma[0] < self.slow_sma[0] and self.fast_sma[-1] > self.slow_sma[-1]:
            #if self.dataclose[0] > (1.20*self.buying_price):
            # We are already in the market, look for a signal to CLOSE trades
            # if len(self) >= (self.bar_executed + 5):
                self.log('CLOSE CREATE {}'.format(self.dataclose[0]))
                self.order = self.close(size=self.size)


class BuyAndHold_1(bt.Strategy):
    def start(self):
        self.val_start = self.broker.get_cash()  # keep the starting cash

    def nextstart(self):
        # Buy all the available cash
        size = int(self.broker.get_cash() / self.data)
        self.buy(size=size)

    def stop(self):
        # calculate the actual returns
        self.roi = (self.broker.get_value() / self.val_start) - 1.0
        print('ROI:        {:.2f}%'.format(100.0 * self.roi))