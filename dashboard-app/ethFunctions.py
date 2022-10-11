import ast
import os
import json
import requests
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import datetime as dt
from web3 import Web3
from dash import html, Input, Output, callback, State, dcc, Dash, dash_table
from pprint import pprint
# from forex_python.converter import CurrencyRates

#######################################################
### REMEMBER NOT TO PUSH THIS CODE ONCE YOU'RE DONE ###
os.environ['WEB3_INFURA_PROJECT_ID'] = 'ad028bbf80ac4032a2c3e1fb6aa6aaa6'
### NOTE: Figure out how to hide project id and other api keys
### in a .env file or the .gitignore document on Github.
#######################################################

# Constants
INFURA_PROJ_ID = os.environ['WEB3_INFURA_PROJECT_ID']


def get_eth_web3():
  ethereum_mainnet_endpoint  = f'https://mainnet.infura.io/v3/{INFURA_PROJ_ID}'
  web3 = Web3(Web3.HTTPProvider(ethereum_mainnet_endpoint))
  assert web3.isConnected()

  return web3

web3 = get_eth_web3()


def block_extracter(time_period):
  """
  This function pulls block data from the Ethereum Blockchain using the time period (in minutes) as the input functions
  and counts backwards. The output will be a raw dictionary list of block data.
  """
  ethBlocks = []
  latest_block = web3.eth.blockNumber
  # time_period = int(input('Input time period (min): '))
  timestamp = int(dt.datetime.timestamp((dt.datetime.now() - dt.timedelta(minutes=time_period))))
  etherscan_endpoint = f'https://api.etherscan.io/api?module=block&action=getblocknobytime&timestamp={timestamp}&closest=before&apikey=YourApiKeyToken'
  etherscan_request = requests.request("GET", url=etherscan_endpoint).text
  etherscan_api_obj = ast.literal_eval(etherscan_request)
  end = int(etherscan_api_obj['result'])
  for i in range(0, end):
    block = web3.eth.getBlock(latest_block - i)
    ethBlocks.append(block)

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

    fig.update_layout(template='plotly_dark', showlegend=True, title=title),

    # Add images
    fig.add_layout_image(
    dict(       
        source="https://raw.githubusercontent.com/ethereum/ethereum-org-website/dev/src/assets/wallet-cropped.png",
        xref="paper",
        yref="paper",
        x=0,
        y=1.75,
        sizex=2,
        sizey=2,
        # sizing="stretch",
        opacity=0.5,
        layer="below")
        ),

    #Adding buttons
    fig.update_xaxes(
          rangeselector=dict(
          buttons=list([
              dict(count=1, label="1min", step="minute", stepmode="backward"),
              dict(count=5, label="5min", step="minute", stepmode="backward"),
              dict(count=15, label="15min", step="minute", stepmode="backward"),
              dict(count=30, label="30min", step="minute", stepmode="backward"),
              # dict(count=1, label="1hr", step="hour", stepmode="backward"),
              # dict(count=1, label="1m", step="month", stepmode="backward"),
              # dict(count=6, label="6m", step="month", stepmode="backward"),
              # dict(count=1, label="YTD", step="year", stepmode="todate"),
              # dict(count=1, label="1y", step="year", stepmode="backward"),
              dict(step="all")
          ]),
          font=dict(color='black'),
          bgcolor='#48cbd9'  #Color scheme taken from website: https://colorswall.com/palette/6108
          )
    ),

    # Updating line color so that it matches the button color.
    fig.update_traces(line_color='#48cbd9')

    return fig

  except KeyError:
    print("Key not found. Make sure that the 'graph_type' is either a box, scatter, line, area, or violin plot")
  except ValueError:
    print("Dimension is not valid. Please check the column names again")