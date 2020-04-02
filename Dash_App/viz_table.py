import dash_table
import dash_html_components as html
import dash_core_components as dcc


def generate_dashtable(dataframe, id_='filtered-datatable', page_size_val=10):
    return dash_table.DataTable(
            id=id_,
            columns=[{"name": i, "id": i} for i in dataframe.columns],
            page_current=0,
            page_size=page_size_val,
            page_action='custom')
