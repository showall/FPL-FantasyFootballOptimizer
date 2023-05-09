import pandas as pd


def calculate_score(df_result):

    df_result = df_result.sort_values("player_total_point_obtained" , ascending=False)
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
    return round(df_all["player_total_point_obtained"].sum(),1)

def calculate_score_table(df_result):
    df_result = df_result.sort_values("player_total_point_obtained" , ascending=False)
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
    return df_all
