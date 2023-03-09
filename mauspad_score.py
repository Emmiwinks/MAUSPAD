import json, grequests, requests
import pandas as pd
from datetime import timedelta


class Mauspad_score:

    def __init__(self, symbol, start, end):
        self.symbol = symbol
        self.start = start
        self.end = end
        print("Starting with", symbol)

        self.key = "tuR59DqzLKEt2G39Q1bLERXRxM1flKOE"
        self.pl = self.get_data_statements("pl")
        self.bs = self.get_data_statements("bs")
        dates = self.bs.index
        self.prices = self.get_data_prices(dates)


    def get_params(self, statement):
        date_range = pd.date_range(self.start, self.end, freq = 'Q').to_period('Q')
        params = []
        for i in date_range:
            year = str(i)[:4]
            quarter = str(i)[4:].lower()
            param = {"api-key": self.key,
                            "ticker": self.symbol,
                            "statement": statement,
                            "fyear": year,
                            "period": quarter} 
            params.append(param)
        return params


    def get_data_statements(self, statement):
        api = "https://simfin.com/api/v2/companies/statements"
        data = []

        params = self.get_params(statement)
        reqs = (grequests.get(api, params=param) for param in params)
        all_reqs = grequests.map(reqs)


        for i in all_reqs:
            load = json.loads(i.text)
            if "error" in str(load):
                print(load)
                exit()
            data.append(load[0]["data"][0])

        df = pd.DataFrame(data, columns=load[0]["columns"]).fillna(0)
        df = df.set_index(pd.to_datetime(df["Report Date"], errors = 'coerce'), drop=True)
        return df


    def get_data_prices(self, dates):
        api = "https://simfin.com/api/v2/companies/prices"
        params = {"api-key": self.key,
                "ticker": self.symbol}
        
        load = json.loads(requests.get(api, params=params).text)
        raw = pd.DataFrame(load[0]["data"], columns=load[0]["columns"]).fillna(0)
        raw["Date"] = pd.to_datetime(raw["Date"], format='%Y-%m-%d', errors = 'coerce')
        raw = raw.set_index(raw["Date"], drop=True)
        final_dates = []
        for date in dates:
            # if quarter's end date not available in prices, find an earlier date as an alternative
            while raw['Date'].eq(date).any() == False:
                date += timedelta(days=-1)
            final_dates.append(date)
        
        df = pd.DataFrame(index=final_dates)
        df = df.join(raw)

        # if quarter's end date price not available, an earlier price is asserted to this date
        # example: 31.12.2022 price is not available - the 30.12.2022 price will be used as the 31.12.2022 price
        df.index = self.bs.index
        
        return df


    def market_cap(self):
        # market capitalization = close price per share * common shares outstanding
        return self.prices["Close"] * self.prices["Common Shares Outstanding"]


    def ev(self):
        # enterprise value = marketCap + totalDebt (short term + long term) - cash
        return self.market_cap() + self.bs["Short Term Debt"] \
            + self.bs["Long Term Debt"] - self.bs["Cash & Cash Equivalents"]


    def ev_mc(self):
        # enterprise value / market capitalization
        return (self.ev() / self.market_cap())# .values[0]


    def netto_debt(self):
        # total debt / total cash
        netto_debt = self.bs["Short Term Debt"] + self.bs["Long Term Debt"] \
                    / self.bs["Cash & Cash Equivalents"]
        return netto_debt


    def ev_ebit(self):
        # ebit = Revenue - COG (cost of goods) - Operating Expenses
        ebit = self.pl["Revenue"] + self.pl["Cost of Revenue"] + self.pl["Operating Expenses"]
        return (self.ev() / ebit)# .values[0]
    

    def net_profit_margin(self):
        # net profit margin = net income * 100 / revenue
        return self.pl["Net Income"] * 100 / self.pl["Revenue"]


    def roe(self):
        # shareholder equity = total assets - total liabilities
        s_equity = self.bs["Total Assets"] - self.bs["Total Liabilities"]
        # return on equity = net income / shareholder equity
        return self.pl["Net Income"] * 100 / s_equity


    def get_score(self, thresholds):
        df = pd.DataFrame(data=[0]*len(self.bs), columns=["score"], index=self.bs.index)

        df['score'] += self.ev_mc().apply(lambda x: 1 if x < thresholds["ev_mc"] else 0)
        df['score'] += self.netto_debt().apply(lambda x: 1 if x < thresholds["netto_debt"] else 0)
        df['score'] += self.ev_ebit().apply(lambda x: 1 if x < thresholds["ev_ebit"] else 0)
        df['score'] += self.net_profit_margin().apply(lambda x: 1 if x > thresholds["net_profit_margin"] else 0)
        df['score'] += self.roe().apply(lambda x: 1 if x > thresholds["roe"] else 0)
        
        return df


if __name__ in '__main__':

    symbol = 'TSLA'
    thresholds = {"ev_mc": 2,
                  "netto_debt": 2,
                  "ev_ebit": 20,
                  "net_profit_margin": 10,
                  "roe": 15}


    m_score = Mauspad_score(symbol, '2012-01-01', '2022-12-31')
    # print("EV/MC: ", m_score.ev_mc())
    # print("Netto Debt", m_score.netto_debt())
    # print("EV/EBIT", m_score.ev_ebit())
    # print("net margin", m_score.net_profit_margin())
    # print("roe", m_score.roe())
    # print("score", m_score.get_score(thresholds))