### Set up ###
# Run the following command:
# `pip install -r utils/requirements-1.txt`
##############

# # Will need to run the dependencies in the "requirements.txt" file: !pip instal -r requirements.txt
# # Installing libraries
import os
import json
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from web3 import Web3
from dash import html, Input, Output, callback, State, dcc, Dash
from pprint import pprint
from datetime import datetime


#######################################################
### REMEMBER NOT TO PUSH THIS CODE ONCE YOU'RE DONE ###
os.environ['WEB3_INFURA_PROJECT_ID'] = 'ad028bbf80ac4032a2c3e1fb6aa6aaa6'
### NOTE: Figure out how to hide project id and other api keys
### in a .env file or the .gitignore document on Github.
#######################################################

# Constants
INFURA_PROJ_ID = os.environ['WEB3_INFURA_PROJECT_ID']



# Building our functions:
## NOTE: If we have a lot of functions, they should probably go inside separate Python scripts you can call and develop modularly

def get_eth_web3():
  ethereum_mainnet_endpoint  = f'https://mainnet.infura.io/v3/{INFURA_PROJ_ID}'
  web3 = Web3(Web3.HTTPProvider(ethereum_mainnet_endpoint))
  assert web3.isConnected()

  return web3

web3 = get_eth_web3()


def block_extracter(answer='yes', number_input=100): # Include "start" again if this function 
  """
  This function pulls block data from the Ethereum Blockchain using block number as the input functions
  and counts backwards. The output will be a raw dictionary list of block data.
  """
  ethBlocks = []
  # answer = input('Are you querying from the most recent block? (yes/no): ')
  try:
    if answer == 'yes':
      latest_block = web3.eth.blockNumber
      # end = int(number_input)
      for i in range(0, int(number_input)):
        block = web3.eth.getBlock(latest_block - i)
        ethBlocks.append(block)
    elif answer == 'no':
      print("Return only 'yes' for now!")
      # start_block = int(input('Specify the starting block number:'))
      # end_block = int(input('Specify the ending block number:'))
      # for i in range(start_block, end_block):
      #   block = web3.eth.getBlock(i)
      #   ethBlocks.append(block)
  except KeyError:
    print("Key not found. Make sure the answer is either 'yes' or 'no.'")

  return ethBlocks


def graphEther(df, kind: str, dimension1: str, dimension2: str, title: str):
  """
  Parameters:
  -----------
  df: Dataframe object
  graph_type: Only graphs available are those in the "plots" dictionary
  dimension1: X-axis
  dimension2: Y-axis
  region: Specified region
  """

  plots = {'box': px.box, 'scatter': px.scatter, 'line': px.line, 'violin': px.violin, 'area': px.area}
  if title == None:
    title = f"{dimension2} over {dimension1}"
  try:
    # Initialize function:
    fig = plots[kind](df, 
                      x=dimension1,
                      y=dimension2,
                      )

    fig.update_layout(template='plotly_dark', showlegend=True, title=title)

    return fig

  except KeyError:
    print("Key not found. Make sure that the 'graph_type' is either a box, scatter, line, area, or violin plot")
  except ValueError:
    print("Dimension is not valid. Please check the column names again")



# ---------------------------------------------------------------------------------------------------------------------------------------------------- #
### Read the data

# web3 = get_eth_web3()


# ---------------------------------------------------------------------------------------------------------------------------------------------------- #
### The App Layout

# Stylesheet
# ext = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Initializing the app
app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
server = app.server

text_style = {
    'textAlign': 'center',
    'color': 'black'
}

card_txt_style =  {
    'textAlign': 'center',
    'color': 'aqua'
}

app.layout = html.Div([                       
                       # The Dropdown Cards
                       html.Div([
                                html.H1("Ethereum Blockchain Analytics Dashboard", style=card_txt_style),
                                 
                        # Dropdown for whether its querying the most recent block.
                                html.P("Are you querying from the most recent block? (yes/no)"),
                                dcc.Dropdown(id='recent-block',
                                             options=[{'label': 'Most Recent', 'value': 'yes'}, 
                                                      {'label': 'Historical Blocks', 'value': 'no'}], 
                                             value='yes'),


                        # Input for how many blocks to analyze
                              html.P("How many blocks back do you want to analyze? (For example: blocksExtracted = latestBlock - n)"),
                              # dbc.Input(id='numeric-input', type="number", min=1, max=200, step=1),
                                dcc.Dropdown(id='numeric-input',
                                                options=[{'label': 'Tens', 'value': '10'},
                                                         {'label': 'Hundreds', 'value': '100'},
                                                         {'label': 'Thousands', 'value': '1000'}],
                                                value='100'),  
                                ]),                       


                       # The graph card
                       html.Div([
                                  html.P("What kind of graph would you like to produce?"),
                                 dcc.Dropdown(
                                     id='graph-type',
                                     options=[{'label': 'Scatter Plot', 'value': 'scatter'},
                                              {'label': 'Line Plot', 'value': 'line'},
                                              {'label': 'Box Plot', 'value': 'box'},
                                              {'label': 'Violin Plot', 'value': 'violin'},
                                              {'label': 'Area Plot', 'value': 'area'}],
                                     value='line'),
                                 ]),
                       dcc.Graph(id='indicator-graphic')
])

# The app.callback is what updates our app so that it's interactive and matches the selections
# on the 'graph-type' dropdown with the graph that's actually rendered below it.

# Callback to update fig
@app.callback(
    Output('indicator-graphic', 'figure'),
    Input('recent-block', 'value'),
    Input('numeric-input', 'value'),
    Input('graph-type', 'value')
) 

def update_figure(answer='yes', number_input='100', graph='line'):
  ethBlocks = block_extracter(answer, number_input)
  eth_block_df = pd.DataFrame(ethBlocks).set_index('number')
  eth_block_df['n_transactions'] = eth_block_df['transactions'].apply(len)
  eth_block_df['datetime'] = eth_block_df['timestamp'].apply(datetime.fromtimestamp)
  fig0 = graphEther(eth_block_df, graph, 'datetime', 'difficulty',  title='ETH Mining Difficulty')
  return fig0


# Adding the following code below to execute the function in an app:

if __name__ == '__main__':

  app.run_server(debug=True, use_reloader=False)