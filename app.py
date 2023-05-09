# Import the necessary libraries
import uvicorn
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import RedirectResponse
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import dash
from dash import dcc
from dash import html
from app2 import app as appco
from get_info import get_info_from_fpl, load_data
from train_model import train_forward_model , train_backward_model
import requests, json
from pprint import pprint
import pandas as pd
import numpy as np
from pyomo.environ import *
import random as rand
from helper import calculate_score, calculate_score_table

import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import base64
import pandas as pd
import dash_mantine_components as dmc

# Define the FastAPI server
app = FastAPI()
# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Define the Dash app
dash_app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
dash_app = appco
#
dashboard_endpoint = "dashboard"
# Mount the Dash app as a sub-application in the FastAPI server
app.mount("/dashboard", WSGIMiddleware(dash_app.server))


# Define the API endpoint to serve data to the Dash app
@app.get("/")
def index():
    # Replace this with your own data retrieval code
    return "Hello"

# Define the API endpoint to serve data to the Dash app
@app.get("/data")
def get_data():
    # Replace this with your own data retrieval code
    data = {"x": [1, 2, 3], "y": [4, 1, 2]}
    return data


@app.get("/load")
def get_data():
    # Put a button on MY DashBoard to link to this url and call for reload
    get_info_from_fpl()
    return RedirectResponse(url="/dashboard")

@app.get("/train/{id}")
def loading_data(id : int):
    # Put a button on MY DashBoard to link to this url and call for train
    # i is to trim the data up to which week. It is important due to the limitations of optimizers.
    df = load_data()
    df = df[df["round"] <= int(id)]    
    model_ = ConcreteModel()
    weekly_score = []
    players_pool = df['identifier'].unique()
    teams = df['team'].unique()
    positions = df['player_position'].unique()
    weeks = df.sort_values("round",ascending = True)['round'].unique()
    model_.x = Var(players_pool, weeks, within=Binary, initialize=0)
    prev_week_selection = []
    selection_hPeriod = []
    selection_Cost = []
    prev_week_selection =[]
    df_result_overall_1 = pd.DataFrame({})    
    print(len(df))
    for week in weeks :
        df_result = pd.DataFrame({})
        df_sub_sub = df[df["round"] == week]
        df_sub_sub.loc[:,"Cost"] =  df_sub_sub.loc[:,"player_costs"]
        for y in range(len(prev_week_selection)) :
            df_sub_sub.loc[df_sub_sub.identifier == prev_week_selection[y],"Cost"] = selection_Cost[y]         
        df_sub_sub.loc[:,"Gain/Loss"]   =  df_sub_sub.loc[:,"player_costs"] - df_sub_sub.loc[:,"Cost"] 
        gain_loss = df_sub_sub.loc[:,"Gain/Loss"].sum()
        print( week, "gain_loss", gain_loss)
        # df_sub_sub.loc[:,"Total_Cost"] = df_sub_sub.loc[:,"Cost"] -  df_sub_sub.loc[:,"Gain/Loss"]
        train_forward_model (df_sub_sub, model_, players_pool,[week], teams, gain_loss, prev_week_selection,  selection_hPeriod) 
        solver = SolverFactory('gurobi')
        results = solver.solve(model_)
        print(f"Week {week}: Objective = {model_.obj():.2f}")
        player_list = []
        for player in players_pool:
            if model_.x[player, week].value == 1:
                print(player, 'is selected in week', week, "HP:",df.loc[((df.identifier== player ) & (df["round"] == week)),"holding_period"].values[0])
                player_list.append(player)
        if player_list == [] :
            break
        df_temp = df_sub_sub[df_sub_sub.identifier.isin(player_list)]
        df_result = pd.concat([df_result,df_temp[df_temp["round"]==week]], axis=0)
        df_result_overall_1 = pd.concat([df_result_overall_1,df_result], axis=0)       
        for i in model_.x:
            if model_.x[i].value == 1 :
                if i[1] == week and i[0] not in prev_week_selection:
                    prev_week_selection.append(i[0]) 
                    selection_hPeriod.append(df[((df.identifier== i[0] ) & (df["round"] == week))]["holding_period"].values[0])
                    selection_Cost.append(df.loc[((df.identifier== i[0] ) & (df["round"] == week)),"player_costs"].values[0])                
    # prev_week_selection = prev_week_selection
        selection_hPeriod = [ x-1 for x in selection_hPeriod ]
        # PURGING     
        negative_indices = [index for index, value in enumerate(selection_hPeriod) if value <= 0]
        for index in sorted(negative_indices, reverse=True):
            prev_week_selection.pop(index)
            selection_hPeriod.pop(index) 
            selection_Cost.pop(index)   
        #   print( prev_week_selection )
        weekly_score.append(calculate_score(df_result))
        print(f"Week {week}: Score = {calculate_score(df_result):.2f}")    
    print(f"TOTAL {week}: Score = {sum(weekly_score):.2f}")
    df_result_overall_1.to_csv("df_tab_2.csv", index= False)     
    model2 = ConcreteModel()
    train_backward_model (df, model2) 

    return RedirectResponse(url="/dashboard")



# Start the FastAPI server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")