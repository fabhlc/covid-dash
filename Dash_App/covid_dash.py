# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import os
from numpy import nan
from datetime import datetime
from viz_table import generate_table
from province_names import prov_names

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


# Load data (date last updated and actual data)
with open(os.path.abspath('../Data/Public_COVID-19_Canada.xlsx'), 'rb') as f:
    update_date = pd.read_excel(f, sheet_name='Cases', index_col=None, header=None, nrows=1)
    update_date = str(update_date.iloc[0, 0])[13:]

with open(os.path.abspath('../Data/Public_COVID-19_Canada.xlsx'), 'rb') as f:
    df = pd.read_excel(f, sheet_name='Cases', index_col=None, skiprows=3, header=0)
    # March 1st onwards
    df = df.loc[df['date_report'] >= datetime.strptime('2020-03-01', '%Y-%m-%d')]
    # Remove repatriated (cruise ships)
    df = df.loc[df['province'] != 'Repatriated']


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1(children=f'COVID-19 Cases in Canada by Date Reported (as of {update_date})'),
    html.Div(children='''Select geography:'''),

    # Dropdown
    html.Div([dcc.Dropdown(id='Province',
                           options=[{'label': prov_names[i],
                                     'value': i
                                     } for i in list(df.province.unique()) + ['All Provinces']],
                           value='All Provinces')],
             style={'width': '25%',
                    'display': 'inline-block'}),
    dcc.Graph(id='funnel-graph'),
    html.H4(children='Individual COVID cases'),
    generate_table(df)
    ])

@app.callback(
    dash.dependencies.Output('funnel-graph', 'figure'),
    [dash.dependencies.Input('Province', 'value')])
def update_graph(prov):
    if prov == "All Provinces":
        df_plot = df.copy()
    else:
        df_plot = df[df['province'] == prov]

    pv = pd.pivot_table(df_plot,
                        index=['date_report'],
                        columns=['province'],
                        values=['case_id'],
                        aggfunc='count',
                        fill_value=nan)

    if prov == 'All Provinces':
        trace1 = go.Bar(x=pv.index, y=pv[('case_id', 'Ontario')], name='Ontario')
        trace2 = go.Bar(x=pv.index, y=pv[('case_id', 'BC')], name='British Columbia')
        trace3 = go.Bar(x=pv.index, y=pv[('case_id', 'Alberta')], name='Alberta')
        trace4 = go.Bar(x=pv.index, y=pv[('case_id', 'Manitoba')], name='Manitoba')
        trace5 = go.Bar(x=pv.index, y=pv[('case_id', 'NL')], name='Newfoundland and Labrador')
        trace6 = go.Bar(x=pv.index, y=pv[('case_id', 'New Brunswick')], name='New Brunswick')
        trace7 = go.Bar(x=pv.index, y=pv[('case_id', 'Quebec')], name='Quebec')
        trace8 = go.Bar(x=pv.index, y=pv[('case_id', 'Yukon')], name='Yukon')
        trace9 = go.Bar(x=pv.index, y=pv[('case_id', 'Saskatchewan')], name='Saskatchewan')
        trace10 = go.Bar(x=pv.index, y=pv[('case_id', 'PEI')], name='Prince Edward Island')
        trace11 = go.Bar(x=pv.index, y=pv[('case_id', 'Nova Scotia')], name='Nova Scotia')
        trace12 = go.Bar(x=pv.index, y=pv[('case_id', 'NWT')], name='Northwest Territories')

        traces = [trace1, trace2, trace3, trace4, trace5, trace6, trace7, trace8, trace9, trace10, trace11, trace12]
    else:
        trace1 = go.Bar(x=pv.index, y=pv[('case_id', prov)], name=prov_names[prov])
        traces = [trace1]

    return {
        'data': traces,
        'layout': go.Layout(
            title=f'Cases in {prov}',
            barmode='stack')
    }

if __name__ == '__main__':
    app.run_server(debug=True)
