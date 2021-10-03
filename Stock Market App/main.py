from urllib.request import urlopen
import json
import pandas as pd
from tickers import tickers, s_p_length
import time
start_time = time.time()

def get_jsonparsed_data(url):

    response = urlopen(url)
    data = response.read().decode("utf-8")
    return json.loads(data)


def clean_number(string):
    if string == '':
        return 0
    else:
        return float(string)



final_list = []
for t in range(0, s_p_length):
    print("% Completed: {:.2f}%".format(t*100/s_p_length))

    ticker = tickers[t]['Symbol']
    name = tickers[t]['Name']
    sector = tickers[t]['Sector']

    print('------Name :  {} ---------'.format(name))
    print('------Ticker :  {} ---------'.format(ticker))
    try:
        d = {'Ticker': ticker, 'Name': name, 'Sector': sector}
        url = ("https://financialmodelingprep.com/api/v3/financial-ratios/{}".format(ticker))
        json_data = get_jsonparsed_data(url)
        number_of_years = len(json_data['ratios'])
        ratios = json_data['ratios']
        d['Latest Year'] = ratios[0]['date']

        income_statement = ('https://financialmodelingprep.com/api/v3/financials/income-statement/{}'.format(ticker))
        income_data = get_jsonparsed_data(income_statement)
        financials = income_data['financials']

        profile = 'https://financialmodelingprep.com/api/v3/company/profile/{}'.format(ticker)
        profile_data = get_jsonparsed_data(profile)
        summary = profile_data['profile']
        d['Market Cap'] = float(summary['mktCap']) / 1000000
        d['52week-low'] = float(summary['range'].split('-')[0])
        d['52week-high'] = float(summary['range'].split('-')[1])
        d['Price'] = float(summary['price'])
        d['% Change from 52week high'] = (d['Price'] - d['52week-high']) / d['52week-high']

        dcf = 'https://financialmodelingprep.com/api/v3/company/discounted-cash-flow/{}'.format(ticker)
        dcf_data = get_jsonparsed_data(dcf)
        d['dcf'] = dcf_data['dcf']

        net_profit_margin_3yrs = 0
        PE = 0
        current_ratio = 0
        debt_to_equity_ratio = 0
        debt_ratio = 0
        net_income = 0
        roe = 0
        times_interest_earned = 0

        if number_of_years > 3:
            d['Years of Data'] = 3
            for i in range(0, 3):
                net_profit_margin_3yrs += clean_number(ratios[i]['profitabilityIndicatorRatios']['netProfitMargin'])
                PE += clean_number(ratios[i]['investmentValuationRatios']['priceEarningsRatio'])
                current_ratio += clean_number(ratios[i]['liquidityMeasurementRatios']['currentRatio'])
                debt_to_equity_ratio += clean_number(ratios[i]['debtRatios']['debtEquityRatio'])
                debt_ratio += clean_number(ratios[i]['debtRatios']['debtRatio'])
                times_interest_earned += clean_number(ratios[0]['debtRatios']['interestCoverage'])
                net_income += clean_number(financials[i]['Net Income'])
                roe += clean_number(ratios[i]['profitabilityIndicatorRatios']['returnOnEquity'])

            d['Avg Net Profit Margin'] = net_profit_margin_3yrs / 3
            d['Avg PE Ratio'] = PE / 3
            d['Avg Current Ratio'] = current_ratio / 3
            d['Avg Debt to Equity Ratio'] = debt_to_equity_ratio / 3
            d['Times Interest Earned'] = times_interest_earned / 3
            d['Avg Debt Ratio'] = debt_ratio / 3
            d['Avg ROE'] = roe / 3
            d['Avg Net Income'] = net_income / 3 / 1000000

        else:
            d['Years of Data'] = 1
            d['Avg Net Profit Margin'] = clean_number(ratios[0]['profitabilityIndicatorRatios']['netProfitMargin'])
            d['Avg PE Ratio'] = clean_number(ratios[0]['investmentValuationRatios']['priceEarningsRatio'])
            d['Avg Current Ratio'] = clean_number(ratios[0]['liquidityMeasurementRatios']['currentRatio'])
            d['Avg Debt to Equity Ratio'] = clean_number(ratios[0]['debtRatios']['debtEquityRatio'])
            d['Avg Debt Ratio'] = clean_number(ratios[0]['debtRatios']['debtRatio'])
            d['Times Interest Earned'] = clean_number(ratios[0]['debtRatios']['interestCoverage'])
            d['Avg ROE'] = clean_number(ratios[0]['profitabilityIndicatorRatios']['returnOnEquity'])
            d['Avg Net Income'] = clean_number(financials[0]['Net Income'])

        final_list.append(d)
    except KeyError:
        continue
    except ValueError:
        continue
    except TypeError:
        continue

df = pd.DataFrame(final_list)
df.to_csv('First Stock Market Valuation v2.csv')
print("time elapsed: {:.2f}s".format(time.time() - start_time))
