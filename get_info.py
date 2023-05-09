import requests, json
from pprint import pprint
import pandas as pd
import numpy as np
from pyomo.environ import *
import random as rand


def get_info_from_fpl():
    print("get_info_from_fpl")
    def get_current_season_history(player_id):
        '''get all past season info for a given player_id'''
        # send GET request to # https://fantasy.premierleague.com/api/element-summary/{PID}/
        try:
            r = requests.get(
                    base_url + 'element-summary/' + str(player_id) + '/'
            ).json()
            # extract 'history_past' data from response into dataframe
            df = pd.json_normalize(r['history'])    

            return df
        except :
            pass

    # base url for all FPL API endpoints
    base_url = 'https://fantasy.premierleague.com/api/'
    r = requests.get(base_url+'bootstrap-static/').json()
    players = r['elements']
    players_df = pd.DataFrame(players)
    column = (list(players_df.drop(["web_name"], axis=1).columns))
    column.insert(0,"web_name") 
    players_df = players_df[column]
    players_df
    teams = pd.json_normalize(r['teams'])
    positions = pd.json_normalize(r['element_types'])
    players = pd.json_normalize(r['elements'])
    fixture_r  = requests.get(base_url + 'fixtures/').json()
    # extract 'history_past' data from response into dataframe
    df_fixture = pd.json_normalize(fixture_r )

    df = pd.merge(
        left=players_df,
        right=teams,
        left_on='team',
        right_on='id'
    )

    # show joined result
    df_player_summary = df.merge(
        positions,
        left_on='element_type',
        right_on='id'
    )

    # rename columns
    df_player_summary  = df_player_summary .rename(
        columns={'singular_name':'position_name'})

    df_players_logs = pd.DataFrame({})
    for i in range (800):
        try:
            df_players_logs= pd.concat([df_players_logs,get_current_season_history(i)], axis=0)
        except:
            pass

    df_fixturez = df_fixture[["event","id","kickoff_time","team_a","team_h","team_h_difficulty","team_a_difficulty"]]

    df_players_logs = pd.merge(
        left=df_players_logs,
        right=df_fixturez,
        left_on='fixture',
        right_on='id'
    )
    df_players_logs["club"] =  df_players_logs["was_home"] *  df_players_logs["team_h"] + (1- df_players_logs["was_home"]) * df_players_logs["team_a"]

    data_df = pd.merge(
    left=df_players_logs,
    right=teams[["id","name"]],
    left_on='club',
    right_on='id'
)
    data_df = data_df.merge(
    players[["id","first_name","photo","second_name","web_name","element_type"]],
    left_on='element',
    right_on='id'
)

    data_df = data_df.merge(
    positions[["id","singular_name"]],
    left_on='element_type',
    right_on='id'
)

    data_df["identifier"] = data_df["web_name"].astype(str) + "-"  + data_df["element"].astype(str) + data_df["club"].astype(str) 

    columns={   "identifier" : "identifier",
                'web_name':'player_name',
                'name':'team',
                'singular_name':'player_position',
                'minutes':'player_minutes_played',
                'total_points':'player_total_point_obtained',
                "round" : "round",
                "value" : "player_costs",
                "second_name" : "second_name",
                "first_name" : "first_name" ,
                "photo" : "photo"
            } 

    data_df  = data_df.rename(columns=
    columns)
    df = data_df[list(columns.values())]

    colnames = df.columns
    na_id = []
    count = 0
    for player_id in df['identifier'].unique():
        count = count + 1
        for gw in range(1, df['round'].max()+1) :
        #    print (count)
        #    print(player_id, gw)
            if df[(df['identifier'] == player_id) & (df['round'] == gw)].empty :
                na_id.append([player_id, gw, 0, 0, 0])

    na_id_df = pd.DataFrame(na_id, columns = ["identifier","round","player_minutes_played","player_total_point_obtained","player_costs"])
    df2 = pd.merge(na_id_df, df[["player_name","identifier","team","player_position","second_name","first_name","photo"]], on="identifier")
    df3= pd.concat([df, df2], axis=0, ignore_index=True)
    df3 = df3.drop_duplicates()

    df.loc[:,"player_costs"] = df.loc[:,"player_costs"]/10
    map_hPeriod = {}
    for x in df["identifier"].unique() :
        map_hPeriod[x] =  rand.randint(1,4)
    df["holding_period"] = df["identifier"].map(map_hPeriod)


    df = df.sort_values(["round","player_minutes_played"], ascending = [True, False])
    df.to_csv("fpl_data.csv", index = False)


def load_data():
    # MAYBE CAN ADD TO LIMIT THE NUMBER OF PLAYERS
    df = pd.read_csv("fpl_data.csv")
    df = df.sort_values(["round","player_minutes_played"], ascending = [True, False])
    for i in range(5):
        df = df.sample(frac=1)
    df = df.sort_values(["round","player_minutes_played"], ascending = [True, False])
    gk_df = df [df["identifier"].isin(df[df.player_position=="Goalkeeper"]["identifier"].unique()[0:10])]
    fw_df = df [df["identifier"].isin(df[df.player_position=="Forward"]["identifier"].unique()[0:20])]
    md_df = df [df["identifier"].isin(df[df.player_position=="Midfielder"]["identifier"].unique()[0:30])]
    df_df = df [df["identifier"].isin(df[df.player_position=="Defender"]["identifier"].unique()[0:20])]
    df = pd.concat([gk_df, fw_df,md_df, df_df], axis = 0)

    # OPTIONAL CHANGE THE COST ABIT TO ENCOURAGE SOLUTIONS
    df.loc[:,"player_costs"] =  df.loc[:,"player_costs"] * ( 1 - df.loc[:,"holding_period"] /100 )

    return df

if __name__ == "__main__":
    get_info_from_fpl()