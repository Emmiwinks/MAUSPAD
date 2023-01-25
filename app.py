from dash import Dash, html, dcc, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

from yfinance import Ticker
from f_score import F_score

app = Dash(__name__)
app.title = 'MAUSPAD'

app.layout = html.Div(children=[
    html.H1(children='Piotrotzki F-Score and more'),

    html.H4("Please enter the stock symbol"),
  
    dcc.Input(id ='text', value ='msft', type ='text'),
    html.Button(id='submit-button-state', type='submit', children='Submit'),

    dcc.Graph(id='f-score-graph')
])

@app.callback(
    Output(component_id='f-score-graph', component_property='figure'),
    Input('submit-button-state', 'n_clicks'),
    State(component_id='text', component_property='value'))
def update_figure(n_clicks, symbol):

    y_ticker = Ticker(symbol)
    f_score = F_score(symbol)

    start = f_score.income_statement.columns[-3]

    f_list = []
    for i in range(len(f_score.income_statement.columns)-2):
        f_score.year_col = i
        f_list.append(f_score.get_piotroski_score())

    price = y_ticker.history(start=start)
    price.index = pd.DatetimeIndex(price.index).date
    f_df = pd.DataFrame(index=pd.DatetimeIndex(f_score.income_statement.columns[0:-2]).date,data=f_list, columns=['f_score'])
    df = pd.concat([price.Close, f_df], axis=1).fillna(method='pad')

    buy_trigger = 7
    sell_trigger = 5

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=df.index, y=df['f_score'], name="F score"),secondary_y=False)
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name="Price", marker_color='black'),secondary_y=True)
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Indicators", secondary_y=False, range=[0,9])
    fig.update_yaxes(title_text="Stock data", secondary_y=True)
    fig.add_hline(y=buy_trigger, annotation_text="Buy trigger", line_dash="dot",line_color="green")
    fig.add_hline(y=sell_trigger, annotation_text="Sell trigger", line_dash="dot",line_color="red")
    # fig.add_hrect(y0=0.9, y1=2.6, line_width=0, fillcolor="red", opacity=0.2)

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)