### Set up ###
# Run the following command:
# `pip install -r utils/requirements-1.txt`
##############

# # Will need to run the dependencies in the "requirements.txt" file: !pip instal -r requirements.txt
# # Installing libraries
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
from dash import html, Input, Output, callback, State, dcc, Dash
from pprint import pprint
from forex_python.converter import CurrencyRates


#######################################################
### REMEMBER NOT TO PUSH THIS CODE ONCE YOU'RE DONE ###
os.environ['WEB3_INFURA_PROJECT_ID'] = 'ad028bbf80ac4032a2c3e1fb6aa6aaa6'
### NOTE: Figure out how to hide project id and other api keys
### in a .env file or the .gitignore document on Github.
#######################################################

# Constants
INFURA_PROJ_ID = os.environ['WEB3_INFURA_PROJECT_ID']
c = CurrencyRates()
usd_cad_exchange = c.get_rate('USD', 'CAD')


# Building our functions:
## NOTE: If we have a lot of functions, they should probably go inside separate Python scripts you can call and develop modularly

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
    # Add images
    fig.add_layout_image(
        dict(       
            source="https://raw.githubusercontent.com/ethereum/ethereum-org-website/dev/src/assets/ethereum-learn.png",
            xref="paper", yref="paper",
            x=0, y=1.75,
            sizex=2, sizey=2,
            # sizing="stretch",
            opacity=0.5, layer="below")
    )

    fig.update_layout(template='plotly_dark', showlegend=True, title=title)

    return fig

  except KeyError:
    print("Key not found. Make sure that the 'graph_type' is either a box, scatter, line, area, or violin plot")
  except ValueError:
    print("Dimension is not valid. Please check the column names again")


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

                                html.H1(
                                  [
                                    # html.Span(
                                    # "Ethereum",
                                    # id="tooltip-target", 
                                    # style={"textDecoration": "underline", "cursor": "pointer"}
                                    # ),
                                    
                                    html.A("Ethereum", href='https://ethereum.org/en/what-is-ethereum/',),

                                    " Blockchain Analytics Dashboard",

                                    html.Abbr(
                                      "\uFE56", 
                                      title="What is Ethereum? Ethereum is a technology that's home to digital money, global payments, and applications. The community has built a booming digital economy, bold new ways for creators to earn online, and so much more. It's open to everyone, wherever you are in the world – all you need is the internet."
                                    ),

                                  ], style=card_txt_style                             
                                  ),

                                  # dbc.Tooltip("\
                                  #   What is Ethereum? \
                                  #   Ethereum is a technology that's home to digital money, global payments, and applications. \
                                  #   The community has built a booming digital economy, bold new ways for creators to earn online, and so much more. \
                                  #   It's open to everyone, wherever you are in the world – all you need is the internet. \
                                  #   ",
                                  # target="tooltip-target",
                                  # style={"text-align": "right"},),

                                  # dcc.Link(
                                  #   href='https://docs.klimadao.finance/references/glossary#tco2',
                                  #   id="tooltip-target", 
                                  #   ),

                        ]),

                       html.Div([
                                html.Div([
                                  dcc.Markdown("""
                                  ## **What is blockchain?**

                                  Each “block” in a **blockchain** is what I like to think of as highly secure records clumped together like mini databases that’s immutable, meaning that the data in it can’t be changed or edited, and is accessible to the public. The “chain” piece included in the name represents the hash function that connects a block to its prior block, often called its **parent**. This connection provides a layer of security because, for example if we wanted to add, edit, or delete any data that’s already been added to the blockchain, we’d also need to change all subsequent blocks which requires the consensus of the network. And by "network," we're referring to a group of nodes (i.e. computers) which are owned and operated by people all over the world that are interested in validating the transactions. 

                                  Once a group of transaction have been validated, they're then clumped together and are added as a new block to the blockchain. **Node validators** facilitate this process by contributing their computational resources and are thus rewarded through the networks' native token. For example, $ETH for the Ethereum network, $BTC for the Bitcoin network, or $BSC for the Binance network. The creation of more tokens as a result of validating the network is a process called **minting**. Currently in Ethereum, miners are rewarded 2 $ETH for each block they mine under proof-of-work. After the merge, the reward issued will depend on a validator's preformance and amount of ether staked. 

                                  Now, in order for data to be recorded and secured in the blockchain, a block must be produced to store that data, otherwise it's sort of floating out in cyberspace waiting to be added to a block. This is where we can get into the different consensus mechanisms such as proof-of-work or proof-of-stake which we can get into another time. These mechanisms autonomously add blocks to the network that helps store the data, secures it, and adds the properties of decentralization which concepts that's often discussed in realms of political theory, economics, group psychology, etc.
                                  """),

                                  dcc.Markdown("""
                                  ## **Understanding Ethereum**

                                  [**Ethereum**](https://ethereum.org/en/developers/docs/intro-to-ethereum/), or **$ETH**, the cryptocurrency is the bounty paid to users who use their computational resources to verify transactions on the network. For product users, $ETH is a medium of exchange for goods and services on Ethereum ledger which keeps a record of the transactions in a decentralized manner. In addition, whenever users are trying to exchange Ethereum, NFTs, and other cryptocurrencies built within the Ethereum ecosystem, there is an equivalent of a "tax" called gas fees that's added to each transaction. These **gas fees** are the economic incentive that users must pay in $ETH to miners in order to validate the transaction on the network. Generally, the higher a user pays in gas fees, the faster it will take to validate the transaction and record it permanently on the blockchain. 
                                  """)
                                ]),

                                html.Div([
                                  # Input for time frame of how many blocks to analyze
                                  html.P("Provide time frame for blocks to analyze:"),
                                  dcc.Dropdown(id='numeric-input',
                                                  options=[{'label': '15 Min', 'value': '15'},
                                                    {'label': '30 Min', 'value': '30'},
                                                    {'label': '1 Hour', 'value': '60'},
                                                    {'label': '3 Hours', 'value': '180'},
                                                    {'label': '12 Hours', 'value': '720'},
                                                    {'label': '1 Day', 'value': '1440'},
                                                    {'label': '7 Days', 'value': '10080'},
                                                    {'label': '1 Month', 'value': '43200'},
                                                    {'label': '3 Months', 'value': '129600'},
                                                    {'label': '1 Year', 'value': '525600'},
                                                    {'label': '3 Years', 'value': '1576800'},
                                                    {'label': '5 Years', 'value': '2628000'}],
                                                  value='15'),  

                                  html.P("What kind of graph would you like to produce?"),
                                  dcc.Dropdown(
                                      id='graph-type',
                                      options=[{'label': 'Scatter Plot', 'value': 'scatter'},
                                                {'label': 'Line Plot', 'value': 'line'},
                                                {'label': 'Box Plot', 'value': 'box'},
                                                {'label': 'Violin Plot', 'value': 'violin'},
                                                {'label': 'Area Plot', 'value': 'area'}],
                                      value='line'),
                                  dcc.Graph(id='indicator-graphic'),
                                 ]),
                                 
                                html.Div([
                                  dcc.Markdown("""
                                    #### Data dictionary for each [Ethereum block](https://ethereum.org/en/developers/docs/blocks/)

                                    Original Features (20):

                                    - `baseFeePerGas`: the minimum fee per gas required for a transaction to be included in the block. This metric determines the amount of ETH **burnt** or removed from circulation in the system. This is an important feature because it prevents validators from manipulating the system by including their own transactions for free while raising the base fee for everyone else, for example.
                                    - `difficulty`: The amount of computational resrouces used to validate the transactions on the blockchain and add a new block to the network. 
                                    - `extraData`: \[DATA] - the "extra data" field of this block.
                                    - `gasLimit`: The max amount you can pay to a validator to process your transaction.
                                    - `gasUsed`: The amount of gas used in the transaction. 
                                    - `hash`: You can think of hash as like an ID number for the individual block itself (What's the difference between this and `mixHash`??).
                                    - `logsBloom`: \[DATA, 256 Bytes] - the bloom filter??? for the logs of the block. `null` when its pending block.
                                    - `miner`: The hash, or the ID, of the node validator on the network. 
                                    - `mixHash`: a unique identifier for that block.
                                    - `nonce`: Think of this as the answer to a very difficult mathematical problem that validators competing with each other to solve as it leads to the creation of a new block. In other words, its a hash that, when combined with the `mixHash`, proves that the block has gone through [proof-of-work](https://ethereum.org/en/developers/docs/consensus-mechanisms/pow/) which is Ethereum's old consensus mechanism.  
                                    - `number`: The sequential number assigned to each new block once its produced.
                                    - `parentHash`: The hash, or the ID, of the block previous to the current one. 
                                    - `receiptsRoot`: \[DATA, 32 Bytes] - the root of the receipts trie of the block. 
                                    - `sha3Uncles`: \[DATA, 32 Bytes] - SHA3 of the uncles data in the block.
                                    - `size`:  integer the size of this block in bytes. Blocks themselves are bounded in size so that each block has a target size of 15 million gas. However, the size of each block will increase or decrease in accordance with network demands, up until the block limit of 30 million gas (2x target block size). The total amount of gas expended by all transactions in the block must be less than the block gas limit (*Block Gas Limit $>$ SUM(Gas Used Per TXN)*). This is important because it ensures that blocks can’t be arbitrarily large. If blocks could be arbitrarily large, then less performant full nodes would gradually stop being able to keep up with the network due to space and speed requirements.
                                    - `stateRoot`:  – the entire state of the system: account balances, contract storage, contract code and account nonces are inside.
                                    - `timestamp`: The time when the block was produced. 
                                    - `totalDifficulty`: the integer of the total difficulty of the chain until this block. (It should be cumulative?)
                                    - `transactions`: This key contains a list of hashes pertaining to the transactions that were processed within this block.
                                    - `transactionsRoot`: \[DATA, 32 Bytes] - the root of the transaction trie of the block.
                                    - `uncles`: Array of uncle hashes.

                                    Below is a sample DataFrame:
                                  """),
                                  # dbc.Table.from_dataframe(df, id='dataframe', striped=True, bordered=True, hover=True)
                                  ])
                        ]),
])


# The app.callback is what updates our app so that it's interactive and matches the selections
# on the 'graph-type' dropdown with the graph that's actually rendered below it.

# Callback to update fig
@app.callback(
    Output('indicator-graphic', 'figure'),
    # Output('dataframe', 'value'),
    Input('numeric-input', 'value'),
    Input('graph-type', 'value')
) 

def update_figure(number_input='15', graph='line'):
  ethBlocks = block_extracter(int(number_input)) # Reads the data
  eth_block_df = pd.DataFrame(ethBlocks).set_index('number') # Converts the JSON-formatted data into DataFrame. --Note: Consider using PySpark.
  eth_block_df['n_transactions'] = eth_block_df['transactions'].apply(len)
  eth_block_df['datetime'] = eth_block_df['timestamp'].apply(dt.datetime.fromtimestamp)
  fig0 = graphEther(eth_block_df, graph, 'datetime', 'difficulty',  title='ETH Mining Difficulty')
  return fig0

# Adding the following code below to execute the function in an app:

if __name__ == '__main__':

  app.run_server(debug=True, use_reloader=False)