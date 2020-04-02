# -*- coding: utf-8 -*-
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import os
from numpy import nan
from datetime import datetime
from province_names import prov_names
import requests

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Get data
covid_case_url = r'https://docs.google.com/spreadsheets/d/1D6okqtBS3S2NRC7GFVHzaZ67DuTw7LX49-fqSLwJyeo/export?format=xlsx'

s = requests.get(covid_case_url).content

update_date = pd.read_excel(s, sheet_name='Cases', index_col=None, header=None, nrows=1)
update_date = str(update_date.iloc[0, 0])[13:]

df = pd.read_excel(s, sheet_name='Cases', index_col=None, skiprows=3, header=0)
# March 1st onwards
df = df.loc[df['date_report'] >= datetime.strptime('2020-03-01', '%Y-%m-%d')]
# Remove repatriated (cruise ships)
df = df.loc[df['province'] != 'Repatriated']
# Keep only key columns
keep_cols = ['provincial_case_id', 'age', 'sex', 'health_region', 'province', 'date_report', 'report_week',
             'travel_yn', 'travel_history_country', 'additional_info']
df = df[keep_cols]


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1(children=f'COVID-19 Cases in Canada by Date Reported (as of {update_date})'),
    html.Div(children='''Select geography:'''),
    # keycards
    dbc.Row(
        [dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [html.H4(children='Canada Total', className="card-title"),
                         html.H2(id='canadatext_subtitle', className="card-subtitle")]
                        ),
                    color="info",
                    inverse=True
                    ),
            width=4),
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [html.H4(children='Provincial Total', className="card-title"),
                     html.H2(id='provtext_subtitle', className="card-subtitle")]
                    ),
                color="info",
                inverse=True),
            width=8)
        ]
    ),
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
    dash_table.DataTable(id='filtered-datatable', page_size=15, page_current=0),
])

@app.callback(
    Output('funnel-graph', 'figure'),
    [Input('Province', 'value')])
def update_graph(prov):
    if prov == "All Provinces":
        df_plot = df.copy()
    else:
        df_plot = df[df['province'] == prov]

    pv = pd.pivot_table(df_plot,
                        index=['date_report'],
                        columns=['province'],
                        values=['provincial_case_id'],
                        aggfunc='count',
                        fill_value=nan)

    if prov == 'All Provinces':
        trace1 = go.Bar(x=pv.index, y=pv[('provincial_case_id', 'Ontario')], name='Ontario')
        trace2 = go.Bar(x=pv.index, y=pv[('provincial_case_id', 'BC')], name='British Columbia')
        trace3 = go.Bar(x=pv.index, y=pv[('provincial_case_id', 'Alberta')], name='Alberta')
        trace4 = go.Bar(x=pv.index, y=pv[('provincial_case_id', 'Manitoba')], name='Manitoba')
        trace5 = go.Bar(x=pv.index, y=pv[('provincial_case_id', 'NL')], name='Newfoundland and Labrador')
        trace6 = go.Bar(x=pv.index, y=pv[('provincial_case_id', 'New Brunswick')], name='New Brunswick')
        trace7 = go.Bar(x=pv.index, y=pv[('provincial_case_id', 'Quebec')], name='Quebec')
        trace8 = go.Bar(x=pv.index, y=pv[('provincial_case_id', 'Yukon')], name='Yukon')
        trace9 = go.Bar(x=pv.index, y=pv[('provincial_case_id', 'Saskatchewan')], name='Saskatchewan')
        trace10 = go.Bar(x=pv.index, y=pv[('provincial_case_id', 'PEI')], name='Prince Edward Island')
        trace11 = go.Bar(x=pv.index, y=pv[('provincial_case_id', 'Nova Scotia')], name='Nova Scotia')
        trace12 = go.Bar(x=pv.index, y=pv[('provincial_case_id', 'NWT')], name='Northwest Territories')

        traces = [trace1, trace2, trace3, trace4, trace5, trace6, trace7, trace8, trace9, trace10, trace11, trace12]
    else:
        trace1 = go.Bar(x=pv.index, y=pv[('provincial_case_id', prov)], name=prov_names[prov])
        traces = [trace1]

    return {
        'data': traces,
        'layout': go.Layout(
            title=f'Cases in {prov}',
            barmode='stack')
    }


@app.callback(
    [Output('filtered-datatable', 'columns'), Output('filtered-datatable', 'data')],
    [Input('Province', 'value')])
def update_graph(prov):
    if prov == "All Provinces":
        df_plot = df.copy()
    else:
        df_plot = df[df['province'] == prov]

    cols = [{"name": i, "id": i} for i in df_plot.columns]
    data_ = df_plot.to_dict('records')
    return cols, data_


# Update keycards
@app.callback(
    [Output("canadatext_subtitle", "children"),
     Output("provtext_subtitle", "children")],
    [Input("Province", "value")])
def update_text(prov):
    canadatext = "{:,}".format(len(df))
    if prov != 'All Provinces':
        provtext = "{:,}".format(sum(df['province'] == prov))
    else:
        provtext = '-'
    return canadatext, provtext


if __name__ == '__main__':
    app.run_server(debug=True,
                   dev_tools_hot_reload_interval=40_000) # reloads every half a day
