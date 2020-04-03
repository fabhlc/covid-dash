import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
from numpy import nan
from province_names import prov_names
from get_covid_data_from_url import get_covid_data
from format_data import group_age, order_agegroups, inverse_order_dict

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

covid_case_url = r'https://docs.google.com/spreadsheets/d/1D6okqtBS3S2NRC7GFVHzaZ67DuTw7LX49-fqSLwJyeo/export?format=xlsx'


df, deaths, update_date = get_covid_data(covid_case_url)

# Clean age group data
for x in [df, deaths]:
    x['age'] = group_age(x['age'])
    x['age_order'] = order_agegroups(x['age'])

app = dash.Dash()

app.layout = html.Div([
    html.H1(children=f'COVID-19 Cases in Canada by Date Reported (as of {update_date})'),
    # keycards
    html.Div(
        dbc.Row(
            [dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [html.H4(children='Canada Total', className="card-title"),
                         html.H2(id='canadatext_subtitle', className="card-subtitle")]),
                    color="info",
                    inverse=True,
                    outline=True),
                md=3),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [html.H4(children='Provincial Total', className="card-title"),
                         html.H2(id='provtext_subtitle', className="card-subtitle")]),
                    color="info",
                    inverse=True,
                    outline=True),
                md=8)
            ],
        className='mb-4')
    ),
    # Dropdown
    html.Div(children='''Select geography:'''),
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
    dcc.Graph(id='agegender-graph'),
    html.Div(children='* - Excluding records where neither sex nor age are reported.',
             style={'color': 'grey', 'fontsize': 9}),

    # Deaths
    html.Div(
        [html.H4(children='Fatal Cases of Covid'),
         dash_table.DataTable(id='death-df', page_size=15, page_current=0),
         dcc.Graph(id='death-graph'),
         html.Div(children='* - Excluding records where neither sex nor age are reported.',
                  style={'color': 'grey', 'fontsize': 9})
         ],
    )
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


# Cases Table
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


# Update age/gender distribution - bar chart
@app.callback(
    Output("agegender-graph", "figure"),
    [Input("Province", "value")])
def update_agegender(prov):
    if prov == 'All Provinces':
        df_plot = df.copy()
        geo_name = 'Canada'
    else:
        df_plot = df[df['province'] == prov]
        geo_name = prov

    # Drop if row doesn't have values for either age or sex
    df_plot = df_plot[~((df_plot['age']=='Not Reported') & (df_plot['sex'] == 'Not Reported'))]

    # Group
    df_plot = df_plot.groupby(['sex', 'age_order'])['provincial_case_id'].count()

    return {
        'data': [
            {'x': df_plot.Female.index, 'y': df_plot.Female.values, 'type': 'bar', 'name': 'female', 'color': 'primary'},
            {'x': df_plot.Male.index, 'y': df_plot.Male.values, 'type': 'bar', 'name': 'male', 'color': 'secondary'},
            {'x': df_plot['Not Reported'].index, 'y': df_plot['Not Reported'].values, 'type': 'bar', 'name': 'NA', 'color': 'grey'}],
        'layout': go.Layout(
            title=f'Breakdown by Age and Gender in {geo_name}*',
            xaxis=dict(tickvals = df_plot.Female.index,
                       ticktext=[inverse_order_dict(i) for i in df_plot.Female.index],
                       title='Age Range')
        )
    }


@app.callback(
    [Output('death-df', 'columns'), Output('death-df', 'data'), Output('death-graph', 'figure')],
    [Input('Province', 'value')])
def update_deathsdf(prov):
    if prov == 'All Provinces':
        death_plot = deaths.copy()
    else:
        death_plot = deaths[deaths['province'] == prov]
    cols = [{"name": i, "id": i} for i in death_plot.columns]
    data_ = death_plot.to_dict('records')

    # Graph
    death_plot = death_plot[~((death_plot['age'] == 'Not Reported') & (death_plot['sex'] == 'Not Reported'))]
    death_plot = death_plot.groupby(['sex', 'age_order'])['death_id'].count()
    death_plot_data = {
        'data': [
                {'x': death_plot.Female.index, 'y': death_plot.Female.values, 'type': 'bar', 'name': 'female', 'color': 'primary'},
                {'x': death_plot.Male.index, 'y': death_plot.Male.values, 'type': 'bar', 'name': 'male', 'color': 'secondary'},
                {'x': death_plot['Not Reported'].index, 'y': death_plot['Not Reported'].values, 'type': 'bar', 'name': 'NA', 'color': 'grey'}],
            'layout': go.Layout(
                title=f'Deaths by Age and Gender in {prov}*',
                xaxis=dict(tickvals = death_plot.Male.index,
                           ticktext=[inverse_order_dict(i) for i in death_plot.Male.index],
                           title='Age Range')
            )
        }

    return cols, data_, death_plot_data


if __name__ == '__main__':
    # df.to_csv('/Users/fabiennechan/Documents/data.csv', index=None)
    # deaths.to_csv('/Users/fabiennechan/Documents/deaths.csv', index=None)
    start_dash = app.run_server(debug=True,
                                dev_tools_hot_reload_interval=40_000) # reloads every half a day
