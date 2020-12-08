import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import numpy as np
import scipy as sp
import chart_studio.plotly as py
import plotly.express as px
import json
import plotly.graph_objects as go
from urllib.request import urlopen
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output



external_stylesheets=[dbc.themes.CYBORG]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server


trends_agesex = pd.read_csv('/Users/calumwalker/github/CovidDashboard/trend_agesex_20201201.csv', parse_dates=['Date'], index_col=0)
total_cases = pd.read_csv('/Users/calumwalker/github/CovidDashboard/total_cases_by_la_20201201.csv')

with urlopen('https://raw.githubusercontent.com/nmwalkers/CovidDashboard/main/final.geojson') as response:
    areasGEO = json.load(response)

df = pd.read_csv("https://raw.githubusercontent.com/nmwalkers/CovidDashboard/main/total_cases_simd_20201203.csv")



del trends_agesex['Sex']
del trends_agesex['SexQF']
del trends_agesex['AgeGroupQF']
del trends_agesex['CumulativePositive']
del trends_agesex['CrudeRatePositive']
del trends_agesex['DailyDeaths']
del trends_agesex['CumulativeDeaths']
del trends_agesex['CrudeRateDeaths']
del trends_agesex['CumulativeNegative']
del trends_agesex['CrudeRateNegative']
del trends_agesex['Country']
import plotly.graph_objects as go
df_15_to_19 = trends_agesex[trends_agesex['AgeGroup']=='15 to 19']
df_20_to_24 = trends_agesex[trends_agesex['AgeGroup']=='20 to 24']
df_25_to_44 = trends_agesex[trends_agesex['AgeGroup']=='25 to 44']
df_45_to_64 = trends_agesex[trends_agesex['AgeGroup']=='45 to 64']
df_65_to_74 = trends_agesex[trends_agesex['AgeGroup']=='65 to 74']
df_75_to_84 = trends_agesex[trends_agesex['AgeGroup']=='75 to 84']
df_85plus = trends_agesex[trends_agesex['AgeGroup']=='85plus']


df_15_to_19 = df_15_to_19.groupby(['Date']).sum()
df_20_to_24 = df_20_to_24.groupby(['Date']).sum()
df_25_to_44 = df_25_to_44.groupby(['Date']).sum()
df_45_to_64 = df_45_to_64.groupby(['Date']).sum()
df_65_to_74 = df_65_to_74.groupby(['Date']).sum()
df_75_to_84 = df_75_to_84.groupby(['Date']).sum()
df_85plus = df_85plus.groupby(['Date']).sum()

df_15_to_19.columns = ['15 to 19']
df_20_to_24.columns = ['20 to 24']
df_25_to_44.columns = ['25 to 44']
df_45_to_64.columns = ['45 to 64']
df_65_to_74.columns = ['65 to 74']
df_75_to_84.columns = ['75 to 84']
df_85plus.columns = ['85+']


from functools import reduce

data_frames = [df_15_to_19, df_20_to_24, df_25_to_44, df_45_to_64, df_65_to_74, df_75_to_84, df_85plus]


df_merged = reduce(lambda  left,right: pd.merge(left,right,on=['Date'],
                                            how='outer'), data_frames)


del total_cases["Date"]
total_cases.set_index('CAName')

fig = px.line(df_merged, x=df_merged.index, y=["15 to 19", "20 to 24", "25 to 44", "45 to 64", "65 to 74", "75 to 84", "85+"])


fig2 = px.choropleth_mapbox(total_cases, geojson=areasGEO, color="TotalCases",
                           locations="CAName", featureidkey="properties.LAD13NM",
                           center={"lat": 56.4907, "lon": -4.2026},
                           mapbox_style="carto-positron", zoom=5)
fig2.update_layout(margin={"r":0,"t":0,"l":0,"b":0})



app.layout = html.Div(children=[
    html.H1(children='Scotland COVID Dashboard'),

    dcc.Graph(
        id='Map',
        figure=fig2
    ),
html.Div([
    dcc.Graph(id='Series',figure=fig)

    ]),

    html.Div([
            html.Label(['Covid Cases']),
            dcc.Dropdown(
                id='my_dropdown',
                options=[
                         {'label': 'TotalPositive', 'value': 'TotalPositive'},
                         {'label': 'CrudeRatePositive', 'value': 'CrudeRatePositive'},
                         {'label': 'TotalDeaths', 'value': 'TotalDeaths'},
                         {'label': 'CrudeRateDeaths', 'value': 'CrudeRateDeaths'},
                         {'label': 'TotalNegative', 'value': 'TotalNegative'},
                         {'label': 'CrudeRateNegative', 'value': 'CrudeRateNegative'}
                ],
                value='CrudeRateNegative',
                multi=False,
                clearable=False,
                style={"width": "50%"}
            ),
        ]),

    html.Div([
        dcc.Graph(id='pie-chart')
    ]),

])

@app.callback(
    Output(component_id='pie-chart', component_property='figure'),
    [Input(component_id='my_dropdown', component_property='value')]
)

def update_graph(my_dropdown):


    piechart=px.pie(df,
            names=df["SIMDQuintile"],
            values=my_dropdown
            )

    return (piechart)



if __name__ == '__main__':
    app.run_server(debug=True)
