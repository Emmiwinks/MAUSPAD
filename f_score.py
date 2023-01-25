import os
from yfinance import Ticker
from alpha_vantage.fundamentaldata import FundamentalData
from pandas import read_csv

def format_alpha_sheets(raw_df):
    df = raw_df[0].T[2:]
    df.columns = list(raw_df[0].T.iloc[0])
    return df

class F_score:
    def __init__(self, symbol):

        self.year_col = 0

        key = '4UEFVZJRMJOOAUST'
        fd = FundamentalData(key,output_format = 'pandas')

        if str(symbol) in os.listdir('data'):
            self.income_statement = read_csv('data/'+str(symbol)+'/'+str(symbol)+'_income_statement_annual.csv', index_col=0)
            self.balance_sheet = read_csv('data/'+str(symbol)+'/'+str(symbol)+'_balance_sheet_annual.csv', index_col=0)
            self.cash_flow = read_csv('data/'+str(symbol)+'/'+str(symbol)+'_cash_flow_annual.csv', index_col=0)

        else:
            self.income_statement = format_alpha_sheets(fd.get_income_statement_annual(symbol))
            self.balance_sheet = format_alpha_sheets(fd.get_balance_sheet_annual(symbol))
            self.cash_flow = format_alpha_sheets(fd.get_cash_flow_annual(symbol))

            os.mkdir('data/'+str(symbol))
            self.income_statement.to_csv('data/'+str(symbol)+'/'+str(symbol)+'_income_statement_annual.csv')
            self.balance_sheet.to_csv('data/'+str(symbol)+'/'+str(symbol)+'_balance_sheet_annual.csv')
            self.cash_flow.to_csv('data/'+str(symbol)+'/'+str(symbol)+'_cash_flow_annual.csv')

    def get_net_income(self):
        return float(self.income_statement.loc['netIncome'][self.year_col])

    def get_roa(self):
        current = float(self.balance_sheet.loc['totalAssets'][self.year_col])
        previous = float(self.balance_sheet.loc['totalAssets'][self.year_col+1])
        av_assets=(current+previous)/2
        return self.get_net_income()/av_assets

    def get_ocf(self):
        return float(self.cash_flow.loc['operatingCashflow'][self.year_col])

    def get_ltdebt(self):
        current = float(self.balance_sheet.loc['longTermDebt'][self.year_col])
        previous = float(self.balance_sheet.loc['longTermDebt'][self.year_col+1])
        return previous - current

    def get_current_ratio(self):
        current_TCA = float(self.balance_sheet.loc['totalCurrentAssets'][self.year_col])
        previous_TCA = float(self.balance_sheet.loc['totalCurrentAssets'][self.year_col+1])
        current_TCL = float(self.balance_sheet.loc['totalCurrentLiabilities'][self.year_col])
        previous_TCL = float(self.balance_sheet.loc['totalCurrentLiabilities'][self.year_col+1])
        ratio1 = current_TCA/ current_TCL
        ratio2 = previous_TCA / previous_TCL
        return ratio1-ratio2

    def get_new_shares(self):
        current = float(self.balance_sheet.loc['commonStock'][self.year_col])
        previous = float(self.balance_sheet.loc['commonStock'][self.year_col+1])
        return current - previous 

    def get_gross_margin(self):
        current = float(self.income_statement.loc['grossProfit'][self.year_col])\
                /float(self.income_statement.loc['totalRevenue'][self.year_col])
        previous =  float(self.income_statement.loc['grossProfit'][self.year_col+1])\
                /float(self.income_statement.loc['totalRevenue'][self.year_col+1])
        return current - previous

    def get_asset_turnover_ratio(self):
        current = float(self.balance_sheet.loc['totalAssets'][self.year_col])
        prev_1 = float(self.balance_sheet.loc['totalAssets'][self.year_col+1])
        prev_2 = float(self.balance_sheet.loc['totalAssets'][self.year_col+2])
        av_assets1=(current+prev_1)/2
        av_assets2=(prev_1+ prev_2)/2
        atr1=float(self.income_statement.loc['totalRevenue'][self.year_col])/av_assets1
        atr2=float(self.income_statement.loc['totalRevenue'][self.year_col+1])/av_assets2
        return atr1-atr2

    def get_piotroski_score(self):
        score=0
        
        if self.get_net_income()>0:
            score +=1

        if self.get_roa()>0:
            score +=1
            
        if self.get_ocf()>0:
            score +=1
            
        if self.get_ocf() > self.get_net_income():
            score +=1
            
        if self.get_ltdebt()>0:
            score +=1
            
        if self.get_current_ratio()>0:
            score +=1
            
        if self.get_new_shares()>0:
            score +=1
            
        if self.get_gross_margin()>0:
            score +=1
            
        if self.get_asset_turnover_ratio()>0:
            score +=1
            
        return score

if __name__ in '__main__':

    symbol = 'tsla'

    y_ticker = Ticker(symbol)
    f_score = F_score(symbol)

    start = f_score.income_statement.columns[-3]
    f_list = []
    for i in range(len(f_score.income_statement.columns)-2):
        f_score.year_col = i
        f_list.append(f_score.get_piotroski_score())

    #    print("The Piotroski F Score is: " + str(f_score.get_piotroski_score()))
    import pandas as pd
    price = y_ticker.history(start=start)
    price.index = pd.DatetimeIndex(price.index).date
    f_df = pd.DataFrame(index=pd.DatetimeIndex(f_score.income_statement.columns[0:-2]).date,data=f_list, columns=['f_score'])
    df = pd.concat([price.Close, f_df], axis=1)#.fillna(method='pad')
