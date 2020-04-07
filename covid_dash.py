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


df, deaths, update_date = get_covid_data(covid_case_url, method_='local')

# Clean age group data
for x in [df, deaths]:
    x['age'] = group_age(x['age'])
    x['age_order'] = order_agegroups(x['age'])

app = dash.Dash()
server = app.server
app.title = 'COVID-19 Dashboard for Canada'


# Define layout
layout = {
    'autosize': True,
    'automargin': True,
    'margin': {'l': 30, 'r': 30, 'b': 20, 't': 40},
    'hovermode': "closest",
    'plot_bgcolor': "#F9F9F9",
    'paper_bgcolor': "#F9F9F9",
    'legend': {'font': {'size': 10}, 'orientation': "h"},
    'title': "Satellite Overview",
    'main_bg': '#ececec',
    'Male': '#bcd2ee',
    'Female': '#6ca6cd',
    'Not Reported': '#cae1ff'
}

colname_dict = {'provincial_case_id': 'Provincial ID', 'age': 'Age Range', 'sex': 'Sex', 'health_region': 'Region',
                'province': 'Province', 'date_report': 'Report Date', 'report_week': 'Week Reported',
                'travel_yn': 'Travel?', 'travel_history_country': 'Country of Travel',
                'additional_info': 'Additional Info', 'age_order': 'Age (order)', 'death_id': 'ID',
                'date_death_report': 'Report Date'}


app.layout = html.Div(
    style={'backgroundColor': layout['main_bg'],
           'textAlign': 'center',
           'font-family': 'arial'},
    children=[
        html.H1(children='COVID-19 Confirmed Cases in Canada by Date Reported'),
        html.H3(children=f'(Last refresh: {update_date})'),
        html.P(children='Built by Fabienne Chan. Data is crowd-sourced and I do not take liability for faulty reporting.'),
        html.A("[Data source]", href="https://docs.google.com/spreadsheets/d/1D6okqtBS3S2NRC7GFVHzaZ67DuTw7LX49-fqSLwJyeo/"),
        html.A("[GitHub]", href="https://github.com/fabhlc/covid-dash"),

        # Dropdown
        html.Div(children='''Select geography:'''),
        html.Div([dcc.Dropdown(id='Province',
                               options=[{'label': prov_names[i],
                                         'value': i
                                         } for i in ['All Provinces'] + sorted(list(df.province.unique()))],
                               value='All Provinces')],
                 style={'width': '25%',
                        'display': 'inline-block'}),
        html.Div([dcc.Dropdown(id='Region',
                               options=[{'label': 'All Regions', 'value': 'All Regions'}],#{'label': i,
                                         # 'value': i
                                         # } for i in listt(set(df['health_region'])) + ['All Regions']],
                               value='All Regions')],
                 style={'width': '25%',
                        'display': 'inline-block'}),

        # keycards
        html.Div(
            dbc.Row(
                [dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [html.H4(children='Canada Total', className="card-title"),
                             html.H1(id='canadatext_subtitle', className="card-subtitle")]),
                        color="info",
                        outline=True)),
                 dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [html.H4(children='Provincial Total', className="card-title"),
                             html.H1(id='provtext_subtitle', className="card-subtitle")]),
                        color="info",
                        outline=True)),
                 dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [html.H4(children='Regional Total', className="card-title"),
                             html.H1(id='reg_total', className="card-subtitle")]),
                        color="info",
                        outline=True))
                 ])
        ),
        dcc.Graph(id='funnel-graph'),
        html.H4(children='Individual COVID cases'),
        dash_table.DataTable(id='filtered-datatable',
                             page_size=15,
                             page_current=0,
                             style_header={'fontWeight': 'bold',
                                           'backgroundColor': '#cdc9c9'},
                             style_data_conditional=[{'if': {'row_index': 'odd'},
                                                     'backgroundColor': '#fffafa'}]),
        dcc.Graph(id='agegender-graph'),
        html.Div(children='* - Excluding records where neither sex nor age are reported.',
                 style={'color': 'grey', 'fontsize': 9}),

        # Deaths
        html.Div(
            [html.H4(children='Fatal Cases of Covid'),
             dash_table.DataTable(id='death-df',
                                  page_size=15,
                                  page_current=0,
                                  style_header={'fontWeight': 'bold',
                                                'backgroundColor': '#cdc9c9'},
                                  style_data_conditional=[{'if': {'row_index': 'odd'},
                                                           'backgroundColor': '#fffafa'}]
                                  ),
             dcc.Graph(id='death-graph'),
             html.Div(children='* - Excluding records where neither sex nor age are reported.',
                      style={'color': 'grey', 'fontsize': 9})
             ],
        )
])

@app.callback(
    Output('funnel-graph', 'figure'),
    [Input('Province', 'value'), Input('Region', 'value')])
def update_graph(prov, region):
    title_addendum = ''
    if prov == "All Provinces":
        df_plot = df.copy()
    else:
        df_plot = df[df['province'] == prov]
        if region != 'All Regions':
            df_plot = df_plot[df_plot['health_region'] == region]
            title_addendum = f' ({region})'

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
            title=f'Cases in {prov}{title_addendum}',
            barmode='stack')
    }


# Always update region to "All Regions" when province is changed.
@app.callback(
    Output("Region", "value"),
    [Input("Province", "value")])
def refresh_region(prov):
    return 'All Regions'


# Update region list to change to region to province's regions
@app.callback(
    Output("Region", "options"),
    [Input("Province", "value")])
def update_region(prov):
    region_list = [{'label': 'All Regions', 'value': 'All Regions'}]
    if prov != 'All Provinces':
        region_list = list(set(df[df['province'] == prov]['health_region']))
        region_list = [{'label': i, 'value': i} for i in ['All Regions'] + sorted(region_list)]
    return region_list

# Cases Table
@app.callback(
    [Output('filtered-datatable', 'columns'), Output('filtered-datatable', 'data')],
    [Input('Province', 'value'), Input('Region', 'value')])
def update_graph(prov, region):
    if prov == "All Provinces":
        df_plot = df.copy()
    else:
        df_plot = df[df['province'] == prov]
        if region != 'All Regions':
            df_plot = df_plot[df_plot['health_region'] == region]

    # Format datetime
    df_plot.loc[:, 'date_report'] = df_plot['date_report'].dt.strftime('%d-%m-%Y')

    # Edit columns (format, drop, rename)
    df_plot.drop(['age_order', 'report_week'], axis=1, inplace=True)

    cols = [{"name": colname_dict[i], "id": i} for i in df_plot.columns]
    data_ = df_plot.to_dict('records')
    return cols, data_


# Update keycards
@app.callback(
    [Output("canadatext_subtitle", "children"),
     Output("provtext_subtitle", "children"),
     Output("reg_total", "children")],
    [Input("Province", "value"),
     Input("Region", "value")])
def update_text(prov, region):
    canadatext = "{:,}".format(len(df))
    provtext = '-'
    reg_total = '-'
    if prov != 'All Provinces':
        provtext = "{:,}".format(sum(df['province'] == prov))
        if region != 'All Regions':
            reg_total = '{:,}'.format(len(df[(df['province'] == prov) & (df['health_region'] == region)]))
    return canadatext, provtext, reg_total


# Update age/gender distribution - bar chart
@app.callback(
    Output("agegender-graph", "figure"),
    [Input("Province", "value"), Input("Region", 'value')])
def update_agegender(prov, region):
    if prov == 'All Provinces':
        df_plot = df.copy()
        geo_name = 'Canada'
    else:
        df_plot = df[df['province'] == prov]
        geo_name = prov
        if region != 'All Regions':
            df_plot = df_plot[df_plot['health_region'] == region]
            geo_name = f"{prov} {(region)}"

    # Drop if row doesn't have values for either age or sex
    df_plot = df_plot[~((df_plot['age']=='Not Reported') & (df_plot['sex'] == 'Not Reported'))]

    # If there are not reported values:
    output_data = []
    tick_vals =[]
    if len(df_plot) > 0:
        # Group
        df_plot = df_plot.groupby(['sex', 'age_order'])['provincial_case_id'].count().unstack(fill_value=0).stack()

        # If gender data exists for province, add to figure data
        for (sx, colour) in [('Female', layout['Female']), ('Male', layout['Male']), ('Not Reported', layout['Not Reported'])]:
            try:
                if sx in [i[0] for i in df_plot.index]:
                    output_data.append({'x': df_plot[sx].index,
                                                 'y': df_plot[sx].values,
                                                 'type': 'bar',
                                                 'name': sx,
                                                 'color': colour})
                    tick_vals = df_plot[sx].index
            except:
                pass
    return {
        'data': output_data,
        'layout': go.Layout(
            title=f'Breakdown by Age and Gender in {geo_name}*',
            xaxis=dict(tickvals=tick_vals,
                       ticktext=[inverse_order_dict(i) for i in tick_vals],
                       title='Age Range')
        )
    }


@app.callback(
    [Output('death-df', 'columns'), Output('death-df', 'data'), Output('death-graph', 'figure')],
    [Input('Province', 'value'), Input('Region', 'value')])
def update_deathsdf(prov, region):
    if_region = ''
    if prov == 'All Provinces':
        death_plot = deaths.copy()
        death_count = len(deaths)
    else:
        death_plot = deaths[deaths['province'] == prov]
        death_count = sum(deaths['province'] == prov)

        if region != 'All Regions':
            death_plot = death_plot[death_plot['health_region'] == region]
            death_count = sum(death_plot['health_region'] == region)
            if_region = f' ({region})'

    cols = [{"name": colname_dict[i], "id": i} for i in death_plot.columns]
    data_ = death_plot.to_dict('records')

    if len(death_plot) > 0:
        # Graph
        death_plot = death_plot[~((death_plot['age'] == 'Not Reported') & (death_plot['sex'] == 'Not Reported'))]
        death_plot = death_plot.groupby(['sex', 'age_order'])['death_id'].count().unstack(fill_value=0).stack()

        # If gender data exists for province, add to figure data
        death_plot_data_data = []
        for (sx, colour) in [('Female', layout['Female']), ('Male', layout['Male']), ('Not Reported', layout['Not Reported'])]:
            if sx in [i[0] for i in death_plot.index]:
                death_plot_data_data.append({'x': death_plot[sx].index,
                                             'y': death_plot[sx].values,
                                             'type': 'bar',
                                             'name': sx,
                                             'color': colour})
                tick_vals = death_plot[sx].index
    else:
        tmp = deaths.groupby(['sex', 'age_order'])['death_id'].count().Male.index
        death_plot_data_data = [{'x': tmp,
                                 'y': [0 for i in tmp], 'type': 'bar', 'name': 'null', 'color': 'primary'}]
        tick_vals = tmp

    death_plot_data = {
        'data': death_plot_data_data,
        'layout': go.Layout(
            title=f'Deaths by Age and Gender in {prov}{if_region}* (Total: {death_count} deaths)',
            xaxis={'tickvals': tick_vals,
                   'ticktext': [inverse_order_dict(i) for i in tick_vals],
                   'title': 'Age Range'}
            )
        }

    return cols, data_, death_plot_data


if __name__ == '__main__':
    app.run_server(debug=True,
                   dev_tools_hot_reload_interval=40_000)