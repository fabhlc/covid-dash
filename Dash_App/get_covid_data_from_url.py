import requests
import pandas as pd
from datetime import datetime

# Get data
covid_case_url = r'https://docs.google.com/spreadsheets/d/1D6okqtBS3S2NRC7GFVHzaZ67DuTw7LX49-fqSLwJyeo/export?format=xlsx'


def get_covid_data(covid_case_url):
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

    return df, update_date