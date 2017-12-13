
# coding: utf-8

# In[1]:

#importing 

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd


# In[2]:

#Loading the data set and splitting the years into seperate columns with sep='\t'

df = pd.read_csv('Final_data.csv')

#Check that it worked:
df.head(5)


# In[ ]:

#renaming the columns for simplicity

df=df.rename(index=str, columns={"UNIT": "unit", "GEO": "geo", "NA_ITEM": "indicator", "Value": "value", "TIME": "year"})
df.head()


# In[ ]:

# Developing a Dashboard with hover element


app = dash.Dash(__name__)
server = app.server
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})



available_indicators = df['indicator'].unique()
available_units = df['unit'].unique()
available_geos = df['geo'].unique()

app.layout = html.Div([
    html.Div([
    # MEASUREMENT  !!
        html.Div([
            html.H2(children='Measurement Unit'),
            dcc.Dropdown(
                id='unit',
                options=[{'label': i, 'value': i} for i in available_units],
                value='Current prices, million euro'
            )], style={'width': '100%', 'display': 'inline-block'}),
        
    # FIRST INDICATOR
        html.Div([
            html.H2(children='First Indicator'),
            dcc.Dropdown(
                id='xaxis_column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='Exports of goods and services'
            ),
            dcc.RadioItems(
                id='xaxis_type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
        ],style={'width': '50%', 'display': 'inline-block'}),
        
     # SECOND INDICATOR
        html.Div([
            html.H2(children='Second Indicator'),
            dcc.Dropdown(
                id='yaxis_column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='Imports of goods and services'
            ),
            dcc.RadioItems(
                id='yaxis_type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
        ], style={'width': '50%', 'float': 'right', 'display': 'inline-block'})
        
    ], style={
        'borderBottom': 'blue',
        'backgroundColor': 'rgb(66, 155, 244)',
        'padding': '10px 5px'
    }),
      # SLIDER
    html.Div(dcc.Slider(
        id='year_slider',
        min=df['year'].min(),
        max=df['year'].max(),
        value=df['year'].max(),
        step=None,
        marks={str(year): str(year) for year in df['year'].unique()}
    ), style={'width': '85%', 'padding': '40px 20px 40px 110px'}),
    
    # SCATTERPLOT  
    html.Div([
        dcc.Graph(
            id='indicator_scatterplot',
            hoverData={'points': [{'customdata': 'Spain'}]}
        )
    ], style={'width': '100%', 'display': 'inline-block', 'padding': '0 20'}),   
    
  
    
    #LINE GRAPH
    html.Div([
        dcc.Graph(id='x-time-series')
    ], style={'display': 'inline-block', 'width': '95%'}),
    
   

])


@app.callback(
    dash.dependencies.Output('indicator_scatterplot', 'figure'),
    [dash.dependencies.Input('xaxis_column', 'value'),
     dash.dependencies.Input('yaxis_column', 'value'),
     dash.dependencies.Input('xaxis_type', 'value'),
     dash.dependencies.Input('yaxis_type', 'value'),
     dash.dependencies.Input('year_slider', 'value'),
     dash.dependencies.Input('unit', 'value')])
def update_graph(xaxis_column_name, yaxis_column_name,
                 xaxis_type, yaxis_type,
                 year_value, unit_value):
    dff = df[df['year'] == year_value]
    dff = dff[dff['unit'] == unit_value]
    
#SCATTERPLOT
    return {
        'data': [go.Scatter(
            x=dff[dff['indicator'] == xaxis_column_name]['value'],
            y=dff[dff['indicator'] == yaxis_column_name]['value'],
            text=dff[dff['indicator'] == yaxis_column_name]['geo'],
            customdata=dff[dff['indicator'] == yaxis_column_name]['geo'],
            mode='markers',
            marker={
                'size': 40,
                'opacity': 0.5,
                'color':'rgba (43, 150, 111, .8)',
                'line': {'width': 0.5, 'color': 'black'}
            }
        )],
        'layout': go.Layout(
            xaxis={
                'title': xaxis_column_name,
                'type': 'linear' if xaxis_type == 'Linear' else 'log'
            },
            yaxis={
                'title': yaxis_column_name,
                'type': 'linear' if yaxis_type == 'Linear' else 'log'
            },
            margin={'l': 100, 'b': 50, 't': 50, 'r': 100},
            height=450,
            hovermode='closest'
        )
    }

#LINE GRAPH

def create_time_series(dff, axis_type, title):
    return {
        'data': [go.Scatter(
            x=dff['year'],
            y=dff['value'],
            mode='lines+markers',
            marker={
            'size': 10,
            'color': 'rgba(43, 150, 111, .8)',
            'line': {'width': 3.0, 'color': 'black'}
            }
        )],
        'layout': {
            'height': 225,
            'margin': {'l': 80, 'b': 30, 'r': 10, 't': 10},
            'annotations': [{
                'x': 0, 'y': 0.85, 'xanchor': 'left', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                'text': title
            }],
            'yaxis': {'type': 'linear' if axis_type == 'Linear' else 'log'},
            'xaxis': {'showgrid': False}
        }
    }


@app.callback(
    dash.dependencies.Output('x-time-series', 'figure'),
    [dash.dependencies.Input('indicator_scatterplot', 'hoverData'),
     dash.dependencies.Input('xaxis_column', 'value'),
     dash.dependencies.Input('xaxis_type', 'value'),
     dash.dependencies.Input('unit', 'value')])
def update_y_timeseries(hoverData, xaxis_column_name, axis_type, unit_value):
    country_name = hoverData['points'][0]['customdata']
    dff = df[df['geo'] == country_name]
    dff = dff[dff['unit'] == unit_value]
    dff = dff[dff['indicator'] == xaxis_column_name]
    title = '<b>{}</b><br>{}'.format(country_name, xaxis_column_name)
    return create_time_series(dff, axis_type, title)



if __name__ == '__main__':
    app.run_server()

