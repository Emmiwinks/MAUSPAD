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

        try:
            self.summary = pd.read_csv("simfin_data/kpi_summary.csv", index_col=0)
        except:
            self.summary = pd.DataFrame(columns=["Symbol"])

        if symbol in self.summary["Symbol"].values:
            print("Symbol is available offline.")
            s_summary = self.summary.loc[self.summary["Symbol"] == symbol].drop(columns=["Symbol"]).transpose()
            self.pl, self.bs, self.prices = s_summary, s_summary, s_summary

        else:
            self.pl = self.get_data_statements("pl")
            self.bs = self.get_data_statements("bs")
            dates = self.bs.index
            self.prices = self.get_data_prices(dates)
            self.save_to_csv()
    

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
        columns = []

        params = self.get_params(statement)
        reqs = (grequests.get(api, params=param) for param in params)
        all_reqs = grequests.map(reqs, size=10)

        for i in all_reqs:
            try:
                load = json.loads(i.text)
            except Exception as error:
                print(error)
                if i == None:
                    print("NoneType object identified.")
                else:
                    print(i.text)

            if "error" in str(load):
                print(load)
                exit()
            elif load[0]["found"] == True:
                data.append(load[0]["data"][0])
                columns = load[0]["columns"]

        df = pd.DataFrame(data, columns=columns)# .fillna(0)
        df = df.set_index(pd.to_datetime(df["Report Date"], errors = 'coerce'), drop=True)
        return df


    def get_data_prices(self, dates):
        api = "https://simfin.com/api/v2/companies/prices"
        params = {"api-key": self.key,
                "ticker": self.symbol}
        
        load = json.loads(requests.get(api, params=params).text)
        if "error" in str(load):
            print(load)
            exit()
        raw = pd.DataFrame(load[0]["data"], columns=load[0]["columns"]).fillna(0)
        raw["Date"] = pd.to_datetime(raw["Date"], format='%Y-%m-%d', errors = 'coerce')
        raw = raw.set_index(raw["Date"], drop=True)
        final_dates = []
        for date in dates:
            # if quarter's end date not available in prices, find an earlier date as an alternative
            while raw["Date"].eq(date).any() == False:
                # if statement values are earlier than any price recorded, skip
                if raw["Date"][0] > date:
                    break
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
        return (self.ev() / self.market_cap())


    def netto_debt(self):
        # total debt / total cash
        netto_debt = self.bs["Short Term Debt"] + self.bs["Long Term Debt"] \
                    / self.bs["Cash & Cash Equivalents"]
        return netto_debt


    def ebit(self):
        # ebit = Revenue - COG (cost of goods) - Operating Expenses
        return self.pl["Revenue"] - self.pl["Cost of Revenue"] - self.pl["Operating Expenses"]


    def ev_ebit(self):
        # ev / ebit
        return self.ev() / self.ebit()
    

    def net_profit_margin(self):
        # net profit margin = net income * 100 / revenue
        return self.pl["Net Income"] * 100 / self.pl["Revenue"]


    def roe(self):
        # shareholder equity = total assets - total liabilities
        s_equity = self.bs["Total Assets"] - self.bs["Total Liabilities"]
        # return on equity = net income / shareholder equity
        return self.pl["Net Income"] * 100 / s_equity


    def get_score(self, thresholds):
        df = pd.DataFrame(data=[0]*len(self.bs), columns=[self.symbol], index=self.bs.index)

        df[self.symbol] += self.ev_mc().apply(lambda x: 1 if x < thresholds["ev_mc"] else 0)
        df[self.symbol] += self.netto_debt().apply(lambda x: 1 if x < thresholds["netto_debt"] else 0)
        df[self.symbol] += self.ev_ebit().apply(lambda x: 1 if x < thresholds["ev_ebit"] else 0)
        df[self.symbol] += self.net_profit_margin().apply(lambda x: 1 if x > thresholds["net_profit_margin"] else 0)
        df[self.symbol] += self.roe().apply(lambda x: 1 if x > thresholds["roe"] else 0)
        
        return df


    def save_to_csv(self):

        kpis = [
            self.prices["Close"].values,
            self.prices["Common Shares Outstanding"].values,
            self.bs["Short Term Debt"].values,
            self.bs["Long Term Debt"].values,
            self.bs["Cash & Cash Equivalents"].values,
            self.bs["Total Assets"].values,
            self.bs["Total Liabilities"].values,
            self.pl["Revenue"].values,
            self.pl["Cost of Revenue"].values,
            self.pl["Operating Expenses"].values,
            self.pl["Net Income"].values,
            self.market_cap().values,
            self.ev().values,
            self.ev_mc().values,
            self.ebit().values,
            self.ev_ebit().values,
            self.netto_debt().values,
            self.net_profit_margin().values,
            self.roe().values,
        ]

        index = [
            "Close",
            "Common Shares Outstanding",
            "Short Term Debt",
            "Long Term Debt",
            "Cash & Cash Equivalents",
            "Total Assets",
            "Total Liabilities",
            "Revenue",
            "Cost of Revenue",
            "Operating Expenses",
            "Net Income",
            "Market Capitalization",
            "Enterprise Value",
            "EV/MC",
            "EBIT",
            "EV/EBIT",
            "Netto Debt",
            "Net Profit Margin",
            "ROE"
        ]
        
        try:
            df = pd.DataFrame(data=kpis, index=index, columns=self.pl.index.format()).round(2)
        except:
            df = pd.DataFrame(data=kpis, index=index, columns=self.bs.index.format()).round(2)

        df.insert(0, 'Symbol', [self.symbol]*len(df))
    
        csv = pd.concat([self.summary, df])
        csv.to_csv("simfin_data/kpi_summary.csv")



if __name__ in '__main__':

    symbols = ['TSLA','GOOG','MSFT','DKNG','NVDA']
    thresholds = {"ev_mc": 2,
                  "netto_debt": 2,
                  "ev_ebit": 20,
                  "net_profit_margin": 10,
                  "roe": 15}

    for symbol in symbols:
        m_score = Mauspad_score(symbol, '2012-01-01', '2022-12-31')
    # print("EV/MC: ", m_score.ev_mc())
    # print("Netto Debt", m_score.netto_debt())
    # print("EV/EBIT", m_score.ev_ebit())
    # print("net margin", m_score.net_profit_margin())
    # print("roe", m_score.roe())
    # print("score", m_score.get_score(thresholds))