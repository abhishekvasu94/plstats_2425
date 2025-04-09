import pandas as pd
import numpy as np
from mplsoccer import Pitch
import streamlit as st


def process_pass_data(df, json_data, is_home):

    if is_home:
        metadata = json_data['home']
        teamId = metadata['teamId']
    else:
        metadata = json_data['away']
        teamId = metadata['teamId']

    max_interval = 0

    type_list = ['Pass', 'KeeperPickup', 'Tackle', 'BallTouch', 'BallRecovery', 'Challenge', 'Goal']

    for interval in metadata["formations"]:
        if interval["endMinuteExpanded"] - interval["startMinuteExpanded"] > max_interval:
            max_interval = interval["endMinuteExpanded"] - interval["startMinuteExpanded"]
            end_interval = interval["endMinuteExpanded"]
            start_interval = interval["startMinuteExpanded"]

    loc_data = df[(df["team_id"] == teamId) & (df["type"].isin(type_list)) & (df["expanded_minute"] > start_interval) & (df["expanded_minute"] < end_interval)]
    pass_data = loc_data[loc_data["type"] == "Pass"]
    df_recipient = df.loc[df.index.intersection(pass_data.index + 1)]

    pass_data["recipient_player"] = df_recipient["player"].values
    pass_data["recipient_player_id"] = df_recipient["player_id"].values
    pass_data["recipient_team"] = df_recipient["team"].values

    successful = pass_data[pass_data["outcome_type"] == "Successful"]    

    average_locations = loc_data.groupby(['player', 'player_id'], as_index=False)[["x", "y"]].mean().reset_index() 
    count_locations = successful.groupby('player')[["x", "y"]].size().reset_index(name="count")

    average_locations = average_locations.merge(count_locations, left_on="player", right_on="player")

    pass_between = successful.groupby(['player_id','recipient_player_id']).size().reset_index(name='pass_count')
    pass_between = pass_between.sort_values('pass_count', ascending=False)

    pass_between= pass_between.merge(average_locations,left_on='player_id', right_on="player_id")
    pass_between= pass_between.merge(average_locations,left_on='recipient_player_id',right_on="player_id",suffixes=['','_end'])

    pass_between = pass_between[pass_between['pass_count']>3]

    return pass_between, average_locations
