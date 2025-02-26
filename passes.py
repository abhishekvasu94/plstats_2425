from ast import literal_eval
import numpy as np
import streamlit as st

def is_progressive(x, y, end_x, end_y):

    start_dist = np.sqrt((105 - x)**2 + (34 - y)**2)
    end_dist = np.sqrt((105 - end_x)**2 + (34 - end_y)**2)
    #mark that passes to own half are not progressive
    thres = 100
    if x < 52.5 and end_x < 52.5:
        thres = 30
    elif x < 52.5 and end_x >= 52.5:
        thres = 10
    elif x >= 52.5 and end_x >= 52.5:
        thres = 5

    if thres > start_dist - end_dist:
        return False
    else:
        return True

def get_angle(x, y, end_x, end_y):

    angle = np.arctan2(end_y - y, end_x - x)
    return angle

def get_progressive_passes(df, team_name, into_final_third=False):

    df = df[(df["team"] == team_name) & (df["type_name"] == "pass") & (df["result_name"] == "success")]
    df["is_progressive"] = df.apply(lambda row: is_progressive(row["start_x"], row["start_y"], row["end_x"], row["end_y"]), axis=1)
    df_progressive = df[df["is_progressive"] == True]
    df_progressive["angle"] = df_progressive.apply(lambda row: get_angle(row["start_x"], row["start_y"], row["end_x"], row["end_y"]), axis=1)

    # df_progressive["x_start"] = df_progressive["location"].apply(lambda x: literal_eval(x)[0])
    # df_progressive["y_start"] = df_progressive["location"].apply(lambda x: literal_eval(x)[1])
    
    # df_progressive["x_end"] = df_progressive["pass_end_location"].apply(lambda x: literal_eval(x)[0])
    # df_progressive["y_end"] = df_progressive["pass_end_location"].apply(lambda x: literal_eval(x)[1])

    if into_final_third:
        df_progressive = df_progressive[df_progressive["x_end"] > 85]

    return df_progressive
