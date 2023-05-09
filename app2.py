import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import base64
import pandas as pd
import dash_mantine_components as dmc
from get_info import load_data
from train_model import train_forward_model
import requests, json
from pprint import pprint
import pandas as pd
import numpy as np
from pyomo.environ import *
import random as rand
from helper import calculate_score
from dash import dash_table
import os

app = dash.Dash(__name__, requests_pathname_prefix='/dashboard/',  external_stylesheets=[dbc.themes.BOOTSTRAP]) 
                #, routes_pathname_prefix='/dashboard/
dashboard_endpoint = "dashboard"

basepic_top_y = 25
df = pd.read_csv("fpl_data.csv")
max_week = max(df["round"])
namelist = df["player_name"].unique().tolist()
df_table = df.rename(columns={"identifier" : "id","player_position":"position","player_minutes_played":"mins_played","player_total_point_obtained":"points", "player_costs" :"cost"
                     })
df_table1  = df_table [df_table["round"]==1]


p_list = []
# CHECK FILE
past_selection_df = pd.DataFrame({})
for p in list(reversed(range(0, max_week))):
    try :
        with open(f"selection-week{p}.csv") as f :
            df_temp = pd.read_csv(f, encoding='latin1')
            past_selection_df = pd.concat([past_selection_df, df_temp])
            p_list.append(p)
    except :
        next

#print(p_list)
past_selection_df = past_selection_df.rename(columns={"id" : "identifier","position":"player_position","mins_played":"player_minutes_played","points":"player_total_point_obtained",  "cost":"player_costs"
                     })



# Define the section header
header = html.Header(
    [        html.H1("My Dashboard"),        html.P("This is a demo of a dashboard with a main container and a sidebar."),    ],
    style={"background-color": "#007bff", "color": "white", "padding": "20px"},
)





# Define the main container and sidebar columns
container = dbc.Container(
    [dbc.Row([dbc.Col( children=[
            dcc.Tabs(id='tabs', value='random', children=[
                dcc.Tab(
                    label='Random',
                    value='random',
                    children=html.Div(className='control-tab', children= [
                    dbc.Row([
                        dbc.Col(dmc.Card(
                            children=[
                                dmc.CardSection(html.Div(
                                    dmc.Text("Random", weight=600, align="center", size="120%"
                                    ), style={"background-color": "yellow"})
                                ),
                                dmc.Group(
                                    [
                                        dmc.Text("Total Points", weight=500),
                                        dmc.Badge(children="", id="pta1", color="blue", variant="light"),
                                    ],
                                    position="apart",
                                    mt="md",
                                    mb="xs",
                                ),
                                dmc.Group(
                                    [
                                        dmc.Text("Cost", weight=500),
                                        dmc.Badge(children="", id="pta2", color="red", variant="light"),
                                    ],
                                    position="apart",
                                    mt="md",
                                    mb="xs",
                                ),
                            ],
                            withBorder=True,
                            shadow="sm",
                            radius="md",
                            style={"width": "88%", "margin": "3%", "margin-top": "2%", "padding": "3%"},
                        ), width=4),
                        dbc.Col(dmc.Card(
                            children=[
                                dmc.CardSection(html.Div(
                                    dmc.Text("Optimizer", weight=600, align="center", size="120%"
                                    ), style={"background-color": "yellow"})
                                ),
                                dmc.Group(
                                    [
                                        dmc.Text("Total Points", weight=500),
                                        dmc.Badge(children="", id="pta3", color="blue", variant="light"),
                                    ],
                                    position="apart",
                                    mt="md",
                                    mb="xs",
                                ),
                                dmc.Group(
                                    [
                                        dmc.Text("Cost", weight=500),
                                        dmc.Badge(children="", id="pta4", color="red", variant="light"),
                                    ],
                                    position="apart",
                                    mt="md",
                                    mb="xs",
                                ),
                            ],
                            withBorder=True,
                            shadow="sm",
                            radius="md",
                            style={"width": "88%", "margin": "3%", "margin-top": "2%", "padding": "3%"},
                        ), width=4),
                        dbc.Col(dmc.Card(
                            children=[
                                dmc.CardSection(html.Div(
                                    dmc.Text("Best", weight=600, align="center", size="120%"
                                    ), style={"background-color": "yellow"})
                                ),
                                dmc.Group(
                                    [
                                        dmc.Text("Total Points", weight=500),
                                        dmc.Badge(children="", id="pta5", color="blue", variant="light"),
                                    ],
                                    position="apart",
                                    mt="md",
                                    mb="xs",
                                ),
                                dmc.Group(
                                    [
                                        dmc.Text("Cost", weight=500),
                                        dmc.Badge(children="", id="pta6", color="red", variant="light"),
                                    ],
                                    position="apart",
                                    mt="md",
                                    mb="xs",
                                ),
                            ],
                            withBorder=True,
                            shadow="sm",
                            radius="md",
                            style={"width": "88%", "margin": "3%", "margin-top": "2%", "padding": "3%"},
                        ), width=4),
                    ]),

                      #  html.H4(className='what-is', children='What is Manhattan Plot?'),
                        html.Div(id="rand-container",  children=[
                        html.Img(src= "assets/field.jpg", style={'height': '83%', 'width': '80%','position': 'absolute','top': f'{basepic_top_y}%', 'left': '5%'})  ,
                          ], 
                       style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', "height" : "80vh"} ,
    
                    ),

                    html.Div(children = [ dbc.Row(
                                            [
                                                dbc.Col(
                                                    dbc.Card(
                                                        [
                                                            dbc.CardBody(
                                                                [
                                                                    html.H4("Remaining Budget", className="remaining-budget"),
                                                                    html.P(id="budget_card"),
                                                                ]
                                                            ),
                                                        ], 
                                                        style={"width": "18rem"}
                                                    ),
                                                    width=4,  # adjust the width to control the horizontal spacing
                                                ),
                                                dbc.Col(
                                                    dbc.Card(
                                                        [
                                                            dbc.CardBody(
                                                                [
                                                                    html.H4("Accrued Score", className="accrued-score"),
                                                                    html.P(id="score_card"),
                                                                ]
                                                            ),
                                                        ], 
                                                        style={"width": "18rem"}
                                                    ),
                                                    width=4,  # adjust the width to control the horizontal spacing
                                                ),
                                                dbc.Col(
                                                    dbc.Card(
                                                        [
                                                            dbc.CardBody(
                                                                [
                                                                    html.H4("Selected Squad Size", className="remaining-budget"),
                                                                    html.P(id="size_card"),
                                                                ]
                                                            ),
                                                        ], 
                                                        style={"width": "18rem"}
                                                    ),
                                                    width=4,  # adjust the width to control the horizontal spacing
                                                ),
                                            ],
                                            justify="around",  # centers the columns and leaves equal space on either side
                                            align="center",  # centers the cards vertically
                                        ),
                        dash_table.DataTable(
                                        id='table_select',
                                        columns=[{'name': i, 'id': i} for i in df_table.columns if i in  ["id","player_name","team","position","holding_period","cost","points","mins_played"]  ],
                                        data=df_table.to_dict('records'),
                                        column_selectable='single',
                                        selected_columns=[],
                                        style_cell={'textAlign': 'center'},
                                        style_data_conditional=[{
                                            'if': {'column_id': 'Checkbox'},
                                            'textAlign': 'center'
                                        }],
                                        filter_action='native', 
                                        editable=True,
                                        row_selectable='multi',
                                        selected_rows=[],
                                        style_table={'overflowX': 'scroll','width': '100%', 'margin': '1%'},
                                        style_data={
                                            'whiteSpace': 'normal',
                                            'height': 'auto',
                                        },
                                        style_header={
                                            'backgroundColor': 'rgb(230, 230, 230)',
                                            'fontWeight': 'bold'
                                        },
                                        style_cell_conditional=[
                                            {
                                                'if': {'column_id': 'Checkbox'},
                                                'textAlign': 'center',
                                                'width': '10%'
                                            } for c in ['Checkbox']
                                        ],
                                        page_size=10,
                                    ),                         html.Div([dbc.Row ([dbc.Col(
                                  [html.Button('Submit Team Selection', 
                                               id='submit-selection-button', n_clicks=0)]), dbc.Col([
                                                                html.Button('Delete All  \nSelection', 
                                               id='delete-selection-button', n_clicks=0)])], style={'width': '50%'} ) 
                                               , html.Div(id='output1'), html.Div(id='output2')],
                                               style={'width': '90%',"position":"relative"} 
                                               ),
                                    ] ,  style={'width': '90%', "top": "120%","position":"absolute", "margin":"auto","padding-left":"3%"}),
                    ], style={'position': 'relative'})
                ),
                dcc.Tab(
                    label='Optimizer',
                    value='optimizer',
                    children=html.Div(className='control-tab', children= [
                    dbc.Row([
                        dbc.Col(dmc.Card(
                            children=[
                                dmc.CardSection(html.Div(
                                    dmc.Text("Random", weight=600, align="center", size="120%"
                                    ), style={"background-color": "yellow"})
                                ),
                                dmc.Group(
                                    [
                                        dmc.Text("Total Points", weight=500),
                                        dmc.Badge(children="", id="ptb1", color="blue", variant="light"),
                                    ],
                                    position="apart",
                                    mt="md",
                                    mb="xs",
                                ),
                                dmc.Group(
                                    [
                                        dmc.Text("Cost", weight=500),
                                        dmc.Badge(children="", id="ptb2", color="red", variant="light"),
                                    ],
                                    position="apart",
                                    mt="md",
                                    mb="xs",
                                ),
                            ],
                            withBorder=True,
                            shadow="sm",
                            radius="md",
                            style={"width": "88%", "margin": "3%", "margin-top": "2%", "padding": "3%"},
                        ), width=4),
                        dbc.Col(dmc.Card(
                            children=[
                                dmc.CardSection(html.Div(
                                    dmc.Text("Optimizer", weight=600, align="center", size="120%"
                                    ), style={"background-color": "yellow"})
                                ),
                                dmc.Group(
                                    [
                                        dmc.Text("Total Points", weight=500),
                                        dmc.Badge(children="", id="ptb3", color="blue", variant="light"),
                                    ],
                                    position="apart",
                                    mt="md",
                                    mb="xs",
                                ),
                                dmc.Group(
                                    [
                                        dmc.Text("Cost", weight=500),
                                        dmc.Badge(children="", id="ptb4", color="red", variant="light"),
                                    ],
                                    position="apart",
                                    mt="md",
                                    mb="xs",
                                ),
                            ],
                            withBorder=True,
                            shadow="sm",
                            radius="md",
                            style={"width": "88%", "margin": "3%", "margin-top": "2%", "padding": "3%"},
                        ), width=4),
                        dbc.Col(dmc.Card(
                            children=[
                                dmc.CardSection(html.Div(
                                    dmc.Text("Best", weight=600, align="center", size="120%"
                                    ), style={"background-color": "yellow"})
                                ),
                                dmc.Group(
                                    [
                                        dmc.Text("Total Points", weight=500),
                                        dmc.Badge(children="", id="ptb5", color="blue", variant="light"),
                                    ],
                                    position="apart",
                                    mt="md",
                                    mb="xs",
                                ),
                                dmc.Group(
                                    [
                                        dmc.Text("Cost", weight=500),
                                        dmc.Badge(children="", id="ptb6", color="red", variant="light"),
                                    ],
                                    position="apart",
                                    mt="md",
                                    mb="xs",
                                ),
                            ],
                            withBorder=True,
                            shadow="sm",
                            radius="md",
                            style={"width": "88%", "margin": "3%", "margin-top": "2%", "padding": "3%"},
                        ), width=4),
                    ]),

                       # html.H4(className='what-is', children='What is Manhattan Plot?'),
                        html.Div(id="opt-container",  children=[
                        html.Img(src= "assets/field.jpg", style={'height': '83%', 'width': '80%','position': 'absolute','top': f'{basepic_top_y}%', 'left': '5%'})   ], 
                       style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', "height" : "80vh"} ,
                    ),
                    ], style={'position': 'relative'})
                ),
                dcc.Tab(
                    label='Best Scenario',
                    value='best',
                    children=html.Div(className='control-tab', children= [
                    dbc.Row([
                        dbc.Col(dmc.Card(
                            children=[
                                dmc.CardSection(html.Div(
                                    dmc.Text("Random", weight=600, align="center", size="120%"
                                    ), style={"background-color": "yellow"})
                                ),
                                dmc.Group(
                                    [
                                        dmc.Text("Total Points", weight=500),
                                        dmc.Badge(children="", id="ptc1", color="blue", variant="light"),
                                    ],
                                    position="apart",
                                    mt="md",
                                    mb="xs",
                                ),
                                dmc.Group(
                                    [
                                        dmc.Text("Cost", weight=500),
                                        dmc.Badge(children="", id="ptc2", color="red", variant="light"),
                                    ],
                                    position="apart",
                                    mt="md",
                                    mb="xs",
                                ),
                            ],
                            withBorder=True,
                            shadow="sm",
                            radius="md",
                            style={"width": "88%", "margin": "3%", "margin-top": "2%", "padding": "3%"},
                        ), width=4),
                        dbc.Col(dmc.Card(
                            children=[
                                dmc.CardSection(html.Div(
                                    dmc.Text("Optimizer", weight=600, align="center", size="120%"
                                    ), style={"background-color": "yellow"})
                                ),
                                dmc.Group(
                                    [
                                        dmc.Text("Total Points", weight=500),
                                        dmc.Badge(children="", id="ptc3", color="blue", variant="light"),
                                    ],
                                    position="apart",
                                    mt="md",
                                    mb="xs",
                                ),
                                dmc.Group(
                                    [
                                        dmc.Text("Cost", weight=500),
                                        dmc.Badge(children="", id="ptc4", color="red", variant="light"),
                                    ],
                                    position="apart",
                                    mt="md",
                                    mb="xs",
                                ),
                            ],
                            withBorder=True,
                            shadow="sm",
                            radius="md",
                            style={"width": "88%", "margin": "3%", "margin-top": "2%", "padding": "3%"},
                        ), width=4),
                        dbc.Col(dmc.Card(
                            children=[
                                dmc.CardSection(html.Div(
                                    dmc.Text("Best", weight=600, align="center", size="120%"
                                    ), style={"background-color": "yellow"})
                                ),
                                dmc.Group(
                                    [
                                        dmc.Text("Total Points", weight=500),
                                        dmc.Badge(children="", id="ptc5", color="blue", variant="light"),
                                    ],
                                    position="apart",
                                    mt="md",
                                    mb="xs",
                                ),
                                dmc.Group(
                                    [
                                        dmc.Text("Cost", weight=500),
                                        dmc.Badge(children="", id="ptc6", color="red", variant="light"),
                                    ],
                                    position="apart",
                                    mt="md",
                                    mb="xs",
                                ),
                            ],
                            withBorder=True,
                            shadow="sm",
                            radius="md",
                            style={"width": "88%", "margin": "3%", "margin-top": "2%", "padding": "3%"},
                        ), width=4),
                    ]),

                       # html.H4(className='what-is', children='What is Manhattan Plot?'),
                        html.Div(id="best-container",  children=[
                        html.Img(src= "assets/field.jpg", style={'height': '83%', 'width': '80%','position': 'absolute','top': f'{basepic_top_y}%', 'left': '5%'})   ], 
                       style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', "height" : "80vh"} ,
                    ),
                        # html.Div([html.P('ManhattanPlot allows you to visualize genome-'
                        #        'wide association studies (GWAS) efficiently. '
                        #        'Using WebGL under the hood, you can interactively '
                        #        'explore overviews of massive datasets comprising '
                        #        'hundreds of thousands of points at once, or '
                        #        'take a closer look at a small subset of your data.'),
                        # html.P('You can adjust the threshold level and the '
                        #        'suggestive line in the "Graph" tab.')], style={'position': 'absolute',"top":"120%"})
                    ], style={'position': 'relative'})
                    
                    # html.Div(className='control-tab', children=[
                    #     html.Div(className='app-controls-block', children=[
                    #         html.Div(
                    #             className='app-controls-name',
                    #             children=[
                    #                 'Threshold value (red)'
                    #             ]
                    #         ),
                    #         dcc.Slider(
                    #             id='mhp-slider-genome',
                    #             className='control-slider',
                    #             vertical=False,
                    #             updatemode='mouseup',
                    #             max=4,
                    #             min=1,
                    #             value=2,
                    #             marks={
                    #                 i + 1: '{}'.format(i + 1)
                    #                 for i in range(4)
                    #             },
                    #             step=0.05
                    #         ),
                    #     ]),
                    #     html.Div(
                    #         className='app-controls-block', children=[
                    #             html.Div(
                    #                 className='app-controls-name',
                    #                 children=[
                    #                     'Suggestive line (purple)',
                    #                 ]
                    #             ),
                    #             dcc.Slider(
                    #                 id='mhp-slider-indic',
                    #                 className='control-slider',
                    #                 vertical=False,
                    #                 updatemode='mouseup',
                    #                 max=4,
                    #                 min=1,
                    #                 value=3,
                    #                 marks={
                    #                     i + 1: '{}'.format(i + 1)
                    #                     for i in range(4)
                    #                 },
                    #                 step=0.05
                    #             )
                    #         ]
                    #     )
                    # ]
                   # )
                )
            ]), 
           # html.H1("Main Container"), html.P("This is the main container."), html.P("It takes up most of the width."),html.P("Resize the window to see the sidebar."),
            ], 
                    className= "six columns" , style={"box-shadow": "1rem 1rem 2rem rgba(0,0,0,0.35)" , "padding": "10px" ,"margin": "10px" }
                ),
                dbc.Col(
                    [html.H1("Sidebar"), 
                     html.P("Your Are Viewing Data For :"), 
                     dcc.Dropdown(['Gameweek 1', 'Gameweek 2', 'Gameweek 3', 'Gameweek 4', 'Gameweek 5', 'Gameweek 6', 'Gameweek 7', 'Gameweek 8','Gameweek 9','Gameweek 10',
                                   'Gameweek 11', 'Gameweek 12', 'Gameweek 13', 'Gameweek 14', 'Gameweek 15', 'Gameweek 16', 'Gameweek 17', 'Gameweek 18','Gameweek 19','Gameweek 20',
                                   'Gameweek 21', 'Gameweek 22', 'Gameweek 23', 'Gameweek 24', 'Gameweek 25', 'Gameweek 26', 'Gameweek 27', 'Gameweek 28','Gameweek 29','Gameweek 30',
                                   'Gameweek 31', 'Gameweek 32', 'Gameweek 33', 'Gameweek 34', 'Gameweek 35', 'Gameweek 36', 'Gameweek 37', 'Gameweek 38'                                   
                                   ], 'Gameweek 1', id='gw-dropdown'),
                     html.P("It takes up 3 columns."), html.P("It has the same height as the main container."),
                     html.Button('Show Comparisons', id='change-style-button', n_clicks=0),        
                    dmc.MultiSelect(
                        label="Pick Your Forwards",
                        id = "id-fw",
                        description="You can select a maximum of 4 Forwards.",
                        data=namelist ,
                        disabled = True,
                      #  maxSelectedValues=3,
                        style={"width": "100%"},
                    ), 
                    dmc.MultiSelect(
                        id = "id-mid",
                        label="Pick Your Midfielders",
                        description="You can select a maximum of 7 Midfielders.",
                        data= namelist ,
                        disabled = True, 
                   #     maxSelectedValues=3,
                        style={"width": "100%"},
                    ),         
                    dmc.MultiSelect(
                        label="Pick Your Defenders",
                        id = "id-df",
                        description="You can select a maximum of 6 Defenders.",
                        data= namelist ,
                        disabled = True, 
                       # maxSelectedValues=3,
                        style={"width": "100%"},
                    ) ,
                    dmc.MultiSelect(
                        id = "id-gk",
                        label="Pick Your Goalies",
                        description="You can select a maximum of 2 Goalkeepers.",
                        data= namelist ,
                        disabled = True, 
                       # maxSelectedValues=3,
                        style={"width": "100%"},
                    ),
                        html.Div([
                        "Selection Exists For Gameweek",
                        dcc.Dropdown(id="gameweek-selection", 
                                     options = [{"label": f"Gameweek {i}", "value": i} for i in  range(1)   ]
                                        , value=  p_list, clearable=True, #disabled = True,
                                     multi=True),
                        ] , style = {"margin-top" : "30%","position":"relative"})

                     ],
                    md=3,
                    style={"background-color": "lightgrey","box-shadow": "1rem 1rem 2rem rgba(0,0,0,0.1)" , "padding": "10px" ,"margin": "10px", "height": "260vh" }, 
                ),
            ]
        ),
    ],
    fluid=True, className="my-container", style={"height": "260vh" }, 
)

# Define the layout with the header and container
app.layout = html.Div([header, container])

@app.callback(Output('rand-container', 'children'),
              Output("opt-container","children"), Output("best-container","children"),
                Output("pta1","children"),
                Output("ptb1","children"),
                Output("ptc1","children"),
                Output("pta2","children"),
                Output("ptb2","children"),
                Output("ptc2","children"),
                Output("pta3","children"),
                Output("ptb3","children"),
                Output("ptc3","children"),
                Output("pta4","children"),
                Output("ptb4","children"),
                Output("ptc4","children"),
                Output("pta5","children"),
                Output("ptb5","children"),
                Output("ptc5","children"),
                Output("pta6","children"),
                Output("ptb6","children"),
                Output("ptc6","children"),
            [Input('change-style-button', 'n_clicks')],
            [State("gw-dropdown", "value")]
            )
def update_image(n_clicks, gameweek):
    week_id = int(gameweek.split(" ")[-1])
#need a dataframe 
    global past_selection_df
    
    df_tab_1  = past_selection_df
    #except:
     #   df_tab_1 = pd.read_csv("data.csv")
    
    df_tab_2 = pd.read_csv("df_tab_2.csv")
    df_tab_3 = pd.read_csv("df_tab_3.csv")
    basepic = html.Img(src= "assets/field.jpg", style={'height': '83%', 'width': '80%','position': 'absolute','top': f'{basepic_top_y}%', 'left': '5%'})     
    def present_table(df_result, week_id ) :
        image_base_url = "https://resources.premierleague.com/premierleague/photos/players/250x250/p"  #p225321.png

        df_result = df_result [ df_result["round"] == week_id ].sort_values("player_total_point_obtained" , ascending=False)
        df_gk = df_result [ df_result["player_position"] == "Goalkeeper"].iloc[0:1]
        df_fw =   df_result [ df_result["player_position"] == "Forward" ].iloc[0:3]
        df_df =   df_result [ df_result["player_position"] == "Defender" ].iloc[0:5]
        df_md =   df_result [ df_result["player_position"] == "Midfielder" ].iloc[0:6]

        df_all = pd.concat([df_fw, df_df, df_md], axis=0).sort_values("player_total_point_obtained" , ascending=False).iloc[0:10]
    
        try:
            fw_count = df_all.value_counts("player_position")["Forward"]
            df_count = df_all.value_counts("player_position")["Defender"]
            md_count = df_all.value_counts("player_position")["Midfielder"]
            df_fw =   df_all[ df_all["player_position"] == "Forward" ].iloc[0:fw_count].reset_index()
            df_df =   df_all[ df_all["player_position"] == "Defender" ].iloc[0:df_count].reset_index()
            df_md =   df_all[ df_all["player_position"] == "Midfielder" ].iloc[0: md_count].reset_index()
            df_all = pd.concat([df_fw, df_df, df_md], axis=0).sort_values("player_total_point_obtained" , ascending=False).iloc[0:10]
        except :
            df_all = pd.concat([df_all.iloc[0:9], df_result [ df_result["player_position"] == "Forward" ].iloc[0:1]], axis=0).sort_values("player_total_point_obtained" , ascending=False).iloc[0:10]
        df_all = pd.concat([df_all, df_gk], axis=0)
    #basepic = html.Img(src= "assets/field.jpg", style={'height': '550px', 'width': '600px','position': 'absolute','top': '5%', 'left': '5%'}) 
   # basepic_top_y = 25

        first_row = []
        first_row_b = []
        for _,i in df_fw.iterrows() :  
            length = len(df_fw) -1 
            sp = max(320 - length * 100 ,100)
            dist_to_first = 320 - sp
            per_width = (dist_to_first*2)/(length + 0.0001)
            ep = min(sp+_*per_width, 320 + dist_to_first)
            label = i.photo
            label = label.replace(".jpg",".png")
            first_row.append(dbc.Col(html.Img(src= f"{image_base_url}{label}", style={'height': '13%', 'width': '10%','position': 'absolute','top': f'{basepic_top_y+5}%', 'left': f'{(ep)/8}%'})) )
            first_row_b.append(dbc.Col(html.P(f"{i.player_name}, {i.player_total_point_obtained}pt", style={"font-size":"2vh","color":"white",'height': '70px', 'width': '70px','position': 'absolute','top': f'{basepic_top_y+5+14}%', 'left': f'{(ep+15)/8}%'})) )
        first_row = dbc.Row(first_row)
        first_row_b = dbc.Row(first_row_b)

        sec_row = []
        sec_row_b = []
        for _,i in df_md.iterrows() :  
            length= len(df_md) - 1
            sp = max(320 - length * 100 ,100)
            dist_to_first = 320 - sp
            per_width = (dist_to_first*2)/(length + 0.0001)
            ep = min(sp+_*per_width, 320 + dist_to_first)
            label = i.photo
            label = label.replace(".jpg",".png")
            sec_row.append(dbc.Col(html.Img(src= f"{image_base_url}{label}", style={'height': '13%', 'width': '10%','position': 'absolute','top': f'{basepic_top_y+25}%', 'left': f'{(ep)/8}%'})) ) 
            sec_row_b.append(dbc.Col(html.P(f"{i.player_name},{i.player_total_point_obtained}pt", style={"font-size":"2vh","color":"white",'height': '70px', 'width': '70px','position': 'absolute','top': f'{basepic_top_y+39}%', 'left': f'{(ep+15)/8}%'})) )
        sec_row = dbc.Row(sec_row)
        sec_row_b = dbc.Row(sec_row_b)

        third_row = []
        third_row_b = []
        for _,i in df_df.iterrows() :  
            length = len(df_df) -1
            sp = max(320 - length * 100 ,100)
            dist_to_first = 320 - sp
            per_width = (dist_to_first*2)/(length + 0.0001)
            ep = min(sp+_*per_width, 320 + dist_to_first)
            label = i.photo
            label = label.replace(".jpg",".png")
            third_row.append(dbc.Col(html.Img(src= f"{image_base_url}{label}", style={'height': '13%', 'width': '10%','position': 'absolute','top': f'{basepic_top_y+47}%', 'left': f'{ep/8}%'})) )
            third_row_b.append(dbc.Col(html.P(f"{i.player_name},{i.player_total_point_obtained}pt", style={"font-size":"2vh","color":"white",'height': '70px', 'width': '70px','position': 'absolute','top': f'{basepic_top_y+60}%', 'left': f'{(ep+15)/8}%'})) ) 
        third_row = dbc.Row(third_row)
        third_row_b = dbc.Row(third_row_b)

        gk_row = []
        gk_row_b = []
        for _,i in df_gk.iterrows() :  
            label = i.photo
            label = label.replace(".jpg",".png")
            gk_row.append(dbc.Col(html.Img(src= f"{image_base_url}{label}", style={'height': '13%', 'width': '10%','position': 'absolute','top': f'{basepic_top_y+64}%', 'left': f'40%'})) )
            gk_row_b.append(dbc.Col(html.P(f"{i.player_name},{i.player_total_point_obtained}pt", style={"font-size":"2vh","color":"white",'height': '70px', 'width': '70px','position': 'absolute','top': f'{basepic_top_y+77}%', 'left': f'{(320+15)/8}%'})) ) 
        gk_row = dbc.Row(gk_row)
        gk_row_b = dbc.Row(gk_row_b)
        final_format = [ basepic, first_row, first_row_b ,sec_row, sec_row_b, third_row, third_row_b, gk_row, gk_row_b]
        return final_format

    df_tab_final_1 =  present_table( df_tab_1, week_id )      
    df_tab_final_2 =  present_table( df_tab_2, week_id )        
    df_tab_final_3 =  present_table( df_tab_3, week_id )     


    def generate_score(df_tab_2):
        total_score_2a = calculate_score( df_tab_2[df_tab_2["round"] == week_id] )
        total_score_2b =   sum(calculate_score( df_tab_2[df_tab_2["round"] == j ]) for j in range (1,max_week+1)) 
        total_score_2 = f"{total_score_2a} / {total_score_2b}"
        total_cost_2a =  round( df_tab_2[df_tab_2["round"] == week_id]["player_costs"].sum()) 
        total_cost_2b =  round(df_tab_2["player_costs"].sum())      
        total_cost_2 =  f'{total_cost_2a} / {total_cost_2b}'

        return total_score_2, total_cost_2

    total_score_1, total_cost_1 = generate_score(df_tab_1)
    total_score_2, total_cost_2 = generate_score(df_tab_2)
    total_score_3, total_cost_3 = generate_score(df_tab_3)

        # html.Img(
        #     src='https://www.example.com/mini-image1.jpg', 
        #     style={'position': 'absolute', 'top': '50px', 'left': '50px', 'height': '50px', 'width': '50px', 'object-fit': 'contain'}
        # ),

    if n_clicks%2 == 0:
        return [basepic ] ,[basepic ] ,[basepic ],"", "", "","","","","", "", "","","","","", "", "","","","",
   # encoded_image = base64.b64encode(open('image.png', 'rb').read())
    else :
        return  df_tab_final_1, df_tab_final_2 , df_tab_final_3, \
            total_score_1,  total_score_1, total_score_1, \
            total_cost_1, total_cost_1, total_cost_1, \
            total_score_2,  total_score_2, total_score_2, \
            total_cost_2, total_cost_2, total_cost_2, \
            total_score_3,  total_score_3, total_score_3, \
            total_cost_3, total_cost_3, total_cost_3     
    

@app.callback(
    Output('table_select', 'data'),
    Output('table_select', 'selected_rows'),
    Output('id-fw', 'value'),
    Output('id-mid', 'value'),
    Output('id-df', 'value'),
    Output('id-gk', 'value'),
    Output('budget_card', 'children'),
    Output('score_card', 'children'),
    Output('size_card', 'children'),
    Input('table_select', 'selected_rows'),
    Input("gw-dropdown", "value"),
    State('table_select', 'data')
)
def update_selected_rows(selected_rows, gw, data):
    # Implement your custom logic here to restrict the selection of rows based on column values.
    # For example, to restrict the selection of rows where Column1=="A" to 3 rows, you could use the following code:
    week_id = int(gw.split(" ")[-1])
    df_table2  = df_table [df_table["round"]==week_id]
    serving = []
    global past_selection_df
    budget =100
    past_selection_df_new = []
    if week_id != 1 :
        past_selection_df_new = past_selection_df[past_selection_df["round"]<week_id] 
        earliest_week = sorted(list(past_selection_df_new["round"]))[0]
        
        for wee in sorted(list(past_selection_df_new["round"].unique())):
            if wee < week_id :
                #print(wee)
                #print(past_selection_df_new)            
                cooling_period = week_id -   wee  
                past_selection_df_new2 = past_selection_df_new[(past_selection_df_new["holding_period"] > cooling_period) & (past_selection_df_new["round"] ==wee)  ]["identifier"]
                for x in past_selection_df_new2 :
                    if x not in serving:
                        serving.append(x)
                    else:
                        next
        for wee in sorted(list(past_selection_df_new["round"].unique())):
            if wee < week_id :
                past_selection_df_new2_id= past_selection_df_new[(past_selection_df_new["round"] ==wee)  ]["identifier"]
                bought = past_selection_df_new[past_selection_df_new["identifier"].isin( past_selection_df_new[(past_selection_df_new["round"] ==wee)]["identifier"]) & (past_selection_df_new["round"] == wee)]["player_costs"].sum()
                print("bought",bought)
                #print(df_table)
                #print(df_table[df_table["id"].isin( past_selection_df_new[(past_selection_df_new["round"] ==wee)  ]["identifier"] )& df_table["round"] == wee+1]["cost"])
                sold = df_table[df_table["id"].isin( list(past_selection_df_new[(past_selection_df_new["round"] ==wee)  ]["identifier"]) )& (df_table["round"] == wee+1)]["cost"].sum()           
                print("sold", sold)
                budget =  round(sold- bought + 100, 2)
            else :
                budget =  100
    print (serving)
    
    #selected_players = df_table2[df_table2.index.isin(selected_rows)]["id"]
    selected_players = [data[i]["id"] for i in selected_rows]
    selected_players.extend(serving)
   # print (selected_players)
    selected_df = df_table2[df_table2.id.isin(selected_players)]
    for t in list(selected_df["team"].unique()):
        #print(sum(selected_df["team"]== team))
        if sum(selected_df["team"]== t) >= 3:         
            df_table2 = df_table2[(df_table2["team"]!=t)  | (df_table2["id"].isin( selected_players))]
    if sum(selected_df["position"]== "Defender") >= 6:         
        df_table2 = df_table2[(df_table2["position"]!="Defender")  | (df_table2["id"].isin( selected_players))]
    if sum(selected_df["position"]== "Midfielder") >= 7:            
        df_table2 = df_table2[(df_table2["position"]!="Midfielder")  | (df_table2["id"].isin( selected_players))]
    if sum(selected_df["position"]== "Goalkeeper") >= 2:            
        df_table2 = df_table2[(df_table2["position"]!="Goalkeeper")  | (df_table2["id"].isin( selected_players))]
    if sum(selected_df["position"]== "Forward") >= 4:            
        df_table2 = df_table2[(df_table2["position"]!="Forward")  | (df_table2["id"].isin( selected_players))]
    if len(selected_df) >= 15:         
        df_table2 = df_table2[(df_table2["position"]=="xxxx")  | (df_table2["id"].isin( selected_players))]
        
    # GOT ANY SELECTION FILE SAVED ???
    if selected_df["cost"].sum() > budget:         
        df_table2 = df_table2[ (df_table2["position"]=="xxxx") | (df_table2["id"].isin( selected_players))]
    df_table2 = df_table2.reset_index()
    selected_rows_2 = df_table2.loc[df_table2['id'].isin(selected_players)].index.tolist()
    #print(selected_players)
    #print(selected_rows_2)

    selected_gk   = selected_df [selected_df ["position"]=="Goalkeeper"]["player_name"].tolist()
    selected_fw   = selected_df [selected_df ["position"]=="Forward"]["player_name"].tolist()
    selected_md   = selected_df [selected_df ["position"]=="Midfielder"]["player_name"].tolist()
    selected_df   = selected_df [selected_df ["position"]=="Defender"]["player_name"].tolist()    

    score_card = df_table2.loc[df_table2['id'].isin(selected_players)]["points"].sum()
    budget_card = budget - df_table2.loc[df_table2['id'].isin(selected_players)]["cost"].sum()
    size_card = f"{len(set(selected_players))}/15"

    return df_table2.to_dict('records') , selected_rows_2 , selected_fw, selected_md, selected_df, selected_gk,  budget_card, score_card, size_card


@app.callback(
    Output('submit-selection-button', 'n_clicks'),
    Output('output1', 'children'),
    Output("gameweek-selection", "value"),
    Output("gameweek-selection", "options"),
    State('table_select', 'data'),    
    State('table_select', 'selected_rows'),
    Input('submit-selection-button', 'n_clicks'),
    State("gw-dropdown", "value"),
    State("gameweek-selection", "value"),
)
def save_data(data, selected, n_clicks,gw, selection):
    if n_clicks == 1: 
        week_id = int(gw.split(" ")[-1])
        if selection != [] :
            selection = sorted(selection)

            if selection[0] <= week_id :
                return  0, f"Records exist. You need to delete record {week_id} first", selection , [{"label": f"Gameweek {i}", "value": i} for i in  selection  ]
            if selection[0] <= week_id - 2 :
                return  0, f"You need to select for gameweek {week_id}", selection , [{"label": f"Gameweek {i}", "value": i} for i in  selection  ]
            elif selection[0] >= week_id :
                return  0, f"You already have data for gameweek {selection[0]}, you cannot backfill selection. Delete the records first.", selection, [{"label": f"Gameweek {i}", "value": i} for i in  selection  ]                                                 
        selection.append(week_id )
        df_table2  = df_table [df_table["round"]==week_id]

        
        selected_players = [data[i]["id"] for i in selected]
        df_selection = df_table2[ df_table2.id.isin(selected_players) ]
        if len(df_selection) > 15 :
            return  0, "Maximum squad size exceeded.",selection, [{"label": f"Gameweek {i}", "value": i} for i in  selection  ]      
        if len(df_selection) < 15 :
            return  0, "You havent completed 15 players.",selection , [{"label": f"Gameweek {i}", "value": i} for i in  selection  ] 
        with open(f"selection-week{week_id}.csv") as f :
            df_selection.to_csv(f , index = False)
        with open("text.txt", "r") as b:
            b.write(gw)
        return 0, f"Selection for Gameweek {week_id } saved. Please proceed to next week.", selection, [{"label": f"Gameweek {i}", "value": i} for i in  selection  ]
    return 0, "", p_list, [{"label": f"Gameweek {i}", "value": i} for i in  p_list ]


# @app.callback(  Output('output2', 'children'),
#     Input('gameweek-selection', 'value'),
#     )

# def remove_data(value):
#     global past_selection_df
#     for i in value :
#       #  print (i)
#         past_selection_df = past_selection_df[past_selection_df["round"].isin(value)]
#        # print( past_selection_df)

#         return "Data Modified/Deleted"
    

@app.callback(  Output('output2', 'children'),
    Output('delete-selection-button', 'n_clicks'),
    Input('delete-selection-button', 'n_clicks'),
    State('gameweek-selection', 'value'),
    )

def delete_data(n_clicks, value):
    if n_clicks == 1:
        for i in list(reversed(value)) :
                # Do something with the file, if necessary
                os.remove(f"selection-week{i}.csv")
            #try:

                #past_selection_df = past_selection_df[past_selection_df["round"].isin(value)]
            #except : 
                #pass
        return "Data Deleted", 0
    return "",0


if __name__ == "__main__":
    app.run_server(debug=True)