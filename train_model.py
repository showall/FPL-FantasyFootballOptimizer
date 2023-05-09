#Lets get some samples data to populate tab 2 and 3 which is using Forward Looking Optimizer and BackWard Looking Optimizer
import requests, json
from pprint import pprint
import pandas as pd
import numpy as np
from pyomo.environ import *
import random as rand


def train_forward_model (df_sub, model, players_pool,weeks, teams, gain_loss, prev_week_selection,  selection_hPeriod) :
    # Define the parameters
    budget = 100 # Million
    max_team_players = 3
    max_starting_defenders = 5
    min_starting_defenders = 3
    min_starting_forwards = 1
    max_starting_forwards = 3
    max_starting_goalkeepers = 1
    max_sub_goalkeepers = 1
    max_starting_players = 11
    squad_size = 15

## FORWARD LOOKING MODEL ARE ONLY PRIVY TO THE INFORMATION UP TO THIS POINT
    def obj_rule(model):
        df_points = df_sub.sort_values("player_total_point_obtained" , ascending=False)
        df_gk = df_points[ df_points["player_position"] == "Goalkeeper"].iloc[0:1]
        df_fw = df_points[ df_points["player_position"] == "Forward" ].iloc[0:3]
        df_df = df_points[ df_points["player_position"] == "Defender" ].iloc[0:5]
        df_md = df_points[ df_points["player_position"] == "Midfielder" ].iloc[0:6]
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
            df_all = pd.concat([df_all.iloc[0:9], df_points [ df_points["player_position"] == "Forward" ].iloc[0:1]], axis=0).sort_values("player_total_point_obtained" , ascending=False).iloc[0:10]
        df_all = pd.concat([df_all, df_gk], axis=0)

        total_point_obtained = sum(df_all.loc[(df_all['identifier'] == player) & (df_all['round'] == week), 'player_total_point_obtained'].values[0] * model.x[player, week]
                                for player in players_pool for week in weeks if not (df_all.loc[(df_all['identifier'] == player) & (df_all['round'] == week)].empty))
        total_cost = sum(df_sub.loc[(df_sub['identifier'] == player) & (df_sub['round'] == week), 'player_costs'].values[0] * model.x[player, week]
                        for player in players_pool for week in weeks if not df_sub.loc[(df_sub['identifier'] == player) & (df_sub['round'] == week)].empty)
        total_holding_P = sum(df_all.loc[(df_all['identifier'] == player) & (df_all['round'] == week), 'holding_period'].values[0] * model.x[player, week]
                                   for player in players_pool for week in weeks if not (df_all.loc[(df_all['identifier'] == player) & (df_all['round'] == week)].empty))       
        objective = total_point_obtained - 0.3 * (budget +  gain_loss - total_cost)  -0.25 *  total_holding_P
        return objective

    try:
        model.del_component(model.obj) 
    except:
        pass

    model.obj = Objective(rule=obj_rule, sense=maximize)    
    
    def budget_constraint2(model, week):
        expr = sum(df_sub.loc[(df_sub['identifier'] == player) & (df_sub['round'] == week), 'player_costs'].values[0] * model.x[player, week]
                for player in players_pool
                if len(df_sub.loc[(df_sub['identifier'] == player) & (df_sub['round'] == week)]) > 0)
        return expr <= budget + gain_loss
    if 'budget_con' in model.component_map(Constraint):
        del model.budget_con
        del model.budget_con_index
    model.budget_con = Constraint(weeks, rule=budget_constraint2) 
    
    max_team_players_con_index3 = [(team, week) for team in teams for week in weeks]
    def max_team_players_constraint(model, team, week):
        return sum(model.x[player, week] for player in players_pool 
        if ((df_sub['identifier'] == player) & (df_sub['round'] == week)).any()
        and df_sub.loc[(df_sub['identifier'] == player) & (df_sub['round'] == week), 'team'].values[0] == team) <= max_team_players
    if 'max_team_players_con' in model.component_map(Constraint):
        del model.max_team_players_con
        del model.max_team_players_con_index
    model.max_team_players_con = Constraint(max_team_players_con_index3, rule=max_team_players_constraint)
    
    def max_defenders_constraint(model, week):
        return sum(model.x[player, week] for player in players_pool if 
            ((((( df_sub['identifier'] == player) & (df_sub['round'] == week)).any()) and
            (df_sub.loc[((df_sub['identifier'] == player) & (df_sub['round'] == week)), 
                        'player_position'].values[0] == 'Defender')) and 
                ((df_sub.loc[((df_sub['identifier'] == player) & (df_sub['round'] == week)), 'player_minutes_played'].values[0] >= 0))))    <= 6
    if 'max_defenders_con' in model.component_map(Constraint):
        del model.max_defenders_con
        del model.max_defenders_con_index
    model.max_defenders_con = Constraint(weeks, rule=max_defenders_constraint)
    
    def min_defenders_constraint(model, week):
        return sum(model.x[player, week] for player in players_pool if 
                ((((( df_sub['identifier'] == player) & (df_sub['round'] == week)).any()) and
                (df_sub.loc[((df_sub['identifier'] == player) & (df_sub['round'] == week)), 
                            'player_position'].values[0] == 'Defender')) and 
                    ((df_sub.loc[((df_sub['identifier'] == player) & (df_sub['round'] == week)), 'player_minutes_played'].values[0] >= 0))))>= 4
    if 'min_defenders_con' in model.component_map(Constraint):
        del model.min_defenders_con
        del model.min_defenders_con_index
    model.min_defenders_con = Constraint(weeks, rule=min_defenders_constraint)  

    # def min_defenders_constraint_2(model, week):
    #     return sum(model.x[player, week] for player in players_pool if 
    #             ((((( df_sub['identifier'] == player) & (df_sub['round'] == week)).any()) and
    #             (df_sub.loc[((df_sub['identifier'] == player) & (df_sub['round'] == week)), 
    #                         'player_position'].values[0] == 'Defender')) and 
    #                 ((df_sub.loc[((df_sub['identifier'] == player) & (df_sub['round'] == week)), 'player_minutes_played'].values[0] > 0))))>= 3
    # if 'min_defenders_con' in model.component_map(Constraint):
    #     del model.min_defenders_con_2
    #     del model.min_defenders_con_index_2
    # model.min_defenders_con_2 = Constraint(weeks, rule=min_defenders_constraint_2)  

    def min_forwards_constraint(model, week):
        return sum(model.x[player, week] for player in players_pool if
                ((((( df_sub['identifier'] == player) & (df_sub['round'] == week)).any()) and
                (df_sub.loc[((df_sub['identifier'] == player) & (df_sub['round'] == week)), 
                            'player_position'].values[0] == 'Forward')) and 
    ((df_sub.loc[((df_sub['identifier'] == player) & (df_sub['round'] == week)), 'player_minutes_played'].values[0] >= 0)))) >= 2
    if 'min_forwards_con' in model.component_map(Constraint):
        del model.min_forwards_con 
        del model.min_forwards_con_index 
    model.min_forwards_con = Constraint(weeks, rule=min_forwards_constraint)


    # def min_forwards_constraint_2(model, week):
    #     return sum(model.x[player, week] for player in players_pool if
    #             ((((( df_sub['identifier'] == player) & (df_sub['round'] == week)).any()) and
    #             (df_sub.loc[((df_sub['identifier'] == player) & (df_sub['round'] == week)), 
    #                         'player_position'].values[0] == 'Forward')) and 
    # ((df_sub.loc[((df_sub['identifier'] == player) & (df_sub['round'] == week)), 'player_minutes_played'].values[0] >= 0)))) >= 2
    # if 'min_forwards_con_2' in model.component_map(Constraint):
    #     del model.min_forwards_con_2 
    #     del model.min_forwards_con_index_2 
    # model.min_forwards_con_2 = Constraint(weeks, rule=min_forwards_constraint_2)

    def max_forwards_constraint(model,week):
        return sum(model.x[player, week] for player in players_pool if 
                ((((( df_sub['identifier'] == player) & (df_sub['round'] == week)).any()) and
                (df_sub.loc[((df_sub['identifier'] == player) & (df_sub['round'] == week)), 
                            'player_position'].values[0] == 'Forward')) and 
    ((df_sub.loc[((df_sub['identifier'] == player) & (df_sub['round'] == week)), 'player_minutes_played'].values[0] >= 0)))) <= 5 
    if 'max_forwards_con' in model.component_map(Constraint):
        del model.max_forwards_con
        del model.max_forwards_con_index 
    model.max_forwards_con = Constraint(weeks, rule=max_forwards_constraint)
    
    def max_starting_goalkeepers_constraint(model,week):
        return sum(model.x[player, week] for player in players_pool if 
                ((((( df_sub['identifier'] == player) & (df_sub['round'] == week)).any()) and
                (df_sub.loc[((df_sub['identifier'] == player) & (df_sub['round'] == week)), 
                            'player_position'].values[0] == 'Goalkeeper')) and 
    ((df_sub.loc[((df_sub['identifier'] == player) & (df_sub['round'] == week)), 'player_minutes_played'].values[0] >= 0)))) == 2
    if 'max_starting_goalkeepers_con' in model.component_map(Constraint):
        del model.max_starting_goalkeepers_con  
        del model.max_starting_goalkeepers_con_index
    model.max_starting_goalkeepers_con = Constraint(weeks, rule=max_starting_goalkeepers_constraint)  

    def cap_squad_number_constraint(model, week):
        return sum(model.x[player, week] for player in players_pool if 
                (((df_sub['identifier'] == player) & (df_sub['round'] == week)).any())) == squad_size
    if 'cap_squad_number_con' in model.component_map(Constraint):
        del model.cap_squad_number_con_index
        del model.cap_squad_number_con

    model.cap_squad_number_con = Constraint(weeks, rule= cap_squad_number_constraint)   
    
    def multi_holding_period_constraint(model, player, week):
        if week <= 1:
            return Constraint.Skip
        else:
            prev_week = week - 1
            if player not in prev_week_selection :
                return Constraint.Skip
            else:
                position_th = prev_week_selection.index(player)
                remaining_holding_period = selection_hPeriod[position_th]
                if not ((df_sub['identifier'] == player) & (df_sub['round'] == week)).any()  :
                    return Constraint.Skip
                else:
                    return sum(model.x[player, t[1]] for t in model.x_index if t[1] >= week and t[1] <= week) >= 1  

    if 'multi_holding_period_con' in model.component_map(Constraint):
        del model.multi_holding_period_con
        del model.multi_holding_period_con_index
        del model.multi_holding_period_con_index_1
        del model.multi_holding_period_con_index_0
    model.multi_holding_period_con = Constraint(players_pool, weeks, rule=multi_holding_period_constraint)


def train_backward_model (dfz, model) :
    # Define the parameters
    budget = 100 # Million
    max_team_players = 3
    max_starting_defenders = 5
    min_starting_defenders = 3
    min_starting_forwards = 1
    max_starting_forwards = 3
    max_starting_goalkeepers = 1
    max_sub_goalkeepers = 1
    max_starting_players = 11
    squad_size = 15
   # model = ConcreteModel()
   # df = df[df["round"] <= weeks]
    df_sub_sub = dfz
    df_sub_sub.loc[:,"Cost"] =  df_sub_sub.loc[:,"player_costs"]
    df_sub = df_sub_sub
    players_pool = df_sub['identifier'].unique()
    teams = df_sub['team'].unique()
    positions = df_sub['player_position'].unique()
    weeks = df_sub['round'].unique()
    model.x = Var(players_pool, weeks, within=Binary, initialize=0)
    model.y = Var(players_pool, weeks, within=Binary, initialize=0)
    
    def obj_rule(model):
        df_all = df_sub
        gain_loss = sum(df_all.loc[(df_all['identifier'] == player) & (df_all['round'] == week), 'player_costs'].values[0] * model.x[player, week]
                                for player in players_pool for week in weeks if week < max(weeks) and not df_all.loc[(df_all['identifier'] == player) & (df_all['round'] == week)].empty)\
                                - sum(df_all.loc[(df_all['identifier'] == player) & (df_all['round'] == week + 1), 'player_costs'].values[0] * model.x[player, week]
                                for player in players_pool for week in weeks if week < max(weeks) and not df_all.loc[(df_all['identifier'] == player) & (df_all['round'] == week+1)].empty) 
        
        total_point_obtained = sum(df_all.loc[(df_all['identifier'] == player) & (df_all['round'] == week), 'player_total_point_obtained'].values[0] * model.x[player, week]
                                for player in players_pool for week in weeks if not df_all.loc[(df_all['identifier'] == player) & (df_all['round'] == week)].empty)
        total_cost = sum(df_sub.loc[(df_sub['identifier'] == player) & (df_sub['round'] == week), 'player_costs'].values[0] * model.x[player, week]
                        for player in players_pool for week in weeks if not df_sub.loc[(df_sub['identifier'] == player) & (df_sub['round'] == week)].empty)
        M = sum(model.y[player, week] for player in players_pool for week in weeks)
        K = sum(model.x[player, week] - model.x[player, week-1] for week in weeks if week >=2 for player in players_pool)
        objective = total_point_obtained - 0.3 * (budget *len(weeks)  - total_cost+  gain_loss) - 1 * M  
        return objective
    try:
        model.del_component(model.obj) 
    except:
        pass
    model.obj = Objective(rule=obj_rule, sense=maximize)   

    def budget_constraint(model, week):
        expr = sum(df_sub.loc[(df_sub['identifier'] == player) & (df_sub['round'] == week), 'player_costs'].values[0] * model.x[player, week]
                for player in players_pool if len(df_sub.loc[(df_sub['identifier'] == player) & (df_sub['round'] == week)]) > 0)
        return expr <= budget
    if 'budget_con' in model.component_map(Constraint):
        del model.budget_con
        del model.budget_con_index
    model.budget_con = Constraint(weeks, rule=budget_constraint)   
    max_team_players_con_index3 = [(team, week) for team in teams for week in weeks]
    def max_team_players_constraint(model, team, week):
        return sum(model.x[player, week] for player in players_pool 
        if ((df_sub['identifier'] == player) & (df_sub['round'] == week)).any()
        and df_sub.loc[(df_sub['identifier'] == player) & (df_sub['round'] == week), 'team'].values[0] == team) <= max_team_players
    if 'max_team_players_con' in model.component_map(Constraint):
        del model.max_team_players_con
        del model.max_team_players_con_index
    model.max_team_players_con = Constraint(max_team_players_con_index3, rule=max_team_players_constraint)

    def max_defenders_constraint(model, week):
        return sum(model.x[player, week] for player in players_pool if 
            ((((( df_sub['identifier'] == player) & (df_sub['round'] == week)).any()) and
            (df_sub.loc[((df_sub['identifier'] == player) & (df_sub['round'] == week)), 
                        'player_position'].values[0] == 'Defender')) and 
                ((df_sub.loc[((df_sub['identifier'] == player) & (df_sub['round'] == week)), 'player_minutes_played'].values[0] > 0))))    <= 5            
    if 'max_defenders_con' in model.component_map(Constraint):
        del model.max_defenders_con
        del model.max_defenders_con_index
    model.max_defenders_con = Constraint(weeks, rule=max_defenders_constraint)

    def min_defenders_constraint(model, week):
        return sum(model.x[player, week] for player in players_pool if 
                ((((( df_sub['identifier'] == player) & (df_sub['round'] == week)).any()) and
                (df_sub.loc[((df_sub['identifier'] == player) & (df_sub['round'] == week)), 
                            'player_position'].values[0] == 'Defender')) and 
                    ((df_sub.loc[((df_sub['identifier'] == player) & (df_sub['round'] == week)), 'player_minutes_played'].values[0] > 0))))>= 3
    if 'min_defenders_con' in model.component_map(Constraint):
        del model.min_defenders_con
        del model.min_defenders_con_index
    model.min_defenders_con = Constraint(weeks, rule=min_defenders_constraint)  

    def min_forwards_constraint(model, week):
        return sum(model.x[player, week] for player in players_pool if
                ((((( df_sub['identifier'] == player) & (df_sub['round'] == week)).any()) and
                (df_sub.loc[((df_sub['identifier'] == player) & (df_sub['round'] == week)), 
                            'player_position'].values[0] == 'Forward')) and 
    ((df_sub.loc[((df_sub['identifier'] == player) & (df_sub['round'] == week)), 'player_minutes_played'].values[0] > 0)))) >= 1
    if 'min_forwards_con' in model.component_map(Constraint):
        del model.min_forwards_con 
        del model.min_forwards_con_index 
    model.min_forwards_con = Constraint(weeks, rule=min_forwards_constraint)

    def max_forwards_constraint(model,week):
        return sum(model.x[player, week] for player in players_pool if 
                ((((( df_sub['identifier'] == player) & (df_sub['round'] == week)).any()) and
                (df_sub.loc[((df_sub['identifier'] == player) & (df_sub['round'] == week)), 
                            'player_position'].values[0] == 'Forward')) and 
    ((df_sub.loc[((df_sub['identifier'] == player) & (df_sub['round'] == week)), 'player_minutes_played'].values[0] > 0)))) <= 3
    if 'max_forwards_con' in model.component_map(Constraint):
        del model.max_forwards_con
        del model.max_forwards_con_index 
    model.max_forwards_con = Constraint(weeks, rule=max_forwards_constraint)

    def max_starting_goalkeepers_constraint(model,week):
        return sum(model.x[player, week] for player in players_pool if 
                ((((( df_sub['identifier'] == player) & (df_sub['round'] == week)).any()) and
                (df_sub.loc[((df_sub['identifier'] == player) & (df_sub['round'] == week)), 
                            'player_position'].values[0] == 'Goalkeeper')) and 
    ((df_sub.loc[((df_sub['identifier'] == player) & (df_sub['round'] == week)), 'player_minutes_played'].values[0] >= 0)))) ==2
    if 'max_starting_goalkeepers_con' in model.component_map(Constraint):
        del model.max_starting_goalkeepers_con  
        del model.max_starting_goalkeepers_con_index
    model.max_starting_goalkeepers_con = Constraint(weeks, rule=max_starting_goalkeepers_constraint)

    # def max_substitute_goalkeepers_constraint(model, week):
    #     return sum( model.x[player, week] for player in players_pool if 
    #             (((((df_sub['identifier'] == player) & (df_sub['round'] == week)).any() and
    #             df_sub.loc[((df_sub['identifier'] == player) & (df_sub['round'] == week)), 
    #                         'player_position'].values[0] == 'Goalkeeper')) and 
    #             (( df_sub.loc[((df_sub['identifier'] == player) & (df_sub['round'] == week)), 'player_minutes_played'].values[0] >= 0)))) ==  max_sub_goalkeepers
    
    # if 'max_substitute_goalkeepers_con' in model.component_map(Constraint):
    #     del model.max_substitute_goalkeepers_con  
    #     del model.max_substitute_goalkeepers_con_index
    # model.max_substitute_goalkeepers_con = Constraint(weeks, rule=max_substitute_goalkeepers_constraint)

    def cap_squad_number_constraint(model, week):
        return sum(model.x[player, week] for player in players_pool if 
                (((df_sub['identifier'] == player) & (df_sub['round'] == week)).any())) == squad_size
    if 'cap_squad_number_con' in model.component_map(Constraint):
        del model.cap_squad_number_con_index
        del model.cap_squad_number_con

    model.cap_squad_number_con = Constraint(weeks, rule= cap_squad_number_constraint)    

    def multi_holding_period_constraintc(model, player, week):
        if week <= 1:
            return Constraint.Skip
        else:
            prev_week = max (week - 1, 1)
        # next_week = week + 1
            if not ((df_sub['identifier'] == player) & (df_sub['round'] == week)).any() :
                return Constraint.Skip
            elif not ((df_sub['identifier'] == player) & (df_sub['round'] == prev_week)).any():
                return Constraint.Skip
            else:
                holding_period = df_sub.loc[((df_sub['identifier'] == player) & (df_sub['round'] == week)),"holding_period"].values[0]
                holding_period =  holding_period
                if holding_period <= 1:
                    return Constraint.Skip
                else:
                    start_time =   max(1, week) # week = 2  # hP = 5
                    end_time = min(max(weeks), week + (holding_period-2)) #6, 2 + 3
                    time_periods = range(start_time, end_time+1)             
                    expr = sum(model.x[player, t] for t in time_periods) #2,3,4,5              
                    return expr >= min(max(weeks)-week +1 , holding_period-1 ) * (model.y[player, week])    

    if 'multi_holding_period_conc' in model.component_map(Constraint):
        del model.multi_holding_period_conc
        del model.multi_holding_period_conc_index
        del model.multi_holding_period_conc_index_1
        del model.multi_holding_period_conc_index_0
    model.multi_holding_period_conc = Constraint(players_pool, weeks, rule=multi_holding_period_constraintc)


    def define_y2(model, player, week):
        prev_week = max (week - 1, 1)
        ### IF PREVIOUS IS NOT THE SAME, DEFINE model.y[player, week] AS 1 
        if week <= 1:
            return sum(model.y[player, w] for w in weeks if w <= week and w >= week ) == 1
        elif week == 2 : 
            expr = model.y[player, week]
            return expr >= sum(model.x[player, w-1] - 0 for w in weeks if w <= week and w >= week)
        else :
            expr = model.y[player, week]
    #      return   expr ==   max (sum(model.x[player, w] - model.x[player, w-1] for w in weeks if w <= week and w >= week), 0)
            return expr >= sum(model.x[player, w-1] - model.x[player, w-2] for w in weeks if w <= week and w >= week)
    model.define_y2 = Constraint(players_pool, weeks, rule= define_y2 )

    df_result = pd.DataFrame({})
    weekly_score = []
    df_result_overall = pd.DataFrame({})
    solver = SolverFactory('gurobi')
    results = solver.solve(model)
    for week in weeks:
        print(f"Week {week}: Objective = {model.obj():.2f}")
        player_list = []
        for player in players_pool:
            if model.x[player, week].value == 1:
                # print(player, 'is selected in week', week, "HP:",df_sub_sub[df_sub_sub.identifier == player]["holding_period"].values[0])
                player_list.append(player)
            df_temp = df_sub_sub[df_sub_sub.identifier.isin(player_list)]
        df_result = pd.concat([df_result,df_temp[df_temp["round"]==week]], axis=0)
        # _ = calculate_score(df_temp[df_temp["round"]==week])
        # weekly_score.append(_)
        # print(f"Week {week}: Score = {_:.2f}")
    df_result_overall = pd.concat([df_result_overall,df_result], axis=0)    
    df_result_overall.to_csv("df_tab_3.csv", index= False)