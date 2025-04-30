import pandas as pd
import json
import numpy as np
import streamlit as st
from matplotlib import pyplot as plt
import socceraction.spadl.utils as spu
from socceraction.spadl.opta import convert_to_actions
from PIL import Image
import boto3

from mplsoccer import VerticalPitch, Pitch

from config import *
from plotting import plot_stats, plot_progressive_passes, plot_danger_shots, plot_pass_network
from utils import draw_pass_map, draw_heat_map
from database import FootballDB, download_from_s3


@st.cache_data
def load_data(filename):
    return pd.read_csv(filename)

def get_score(score, home_team, away_team):

    home_goals, away_goals = score.split(" : ")

    text_string = f"{home_team} {home_goals} - {away_goals} {away_team}"

    st.markdown("""
    <style>
    .big-font {
    font-size:30px !important;
    text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

    markdown_string = f"<p class='big-font'> {text_string} </p>"

    st.markdown(markdown_string, unsafe_allow_html=True)



@st.fragment
def render_player_graphs(df):

    with st.form("my-key"):
        selected_player = st.selectbox(
                "Player name",
                df["player"].unique(),
                index=None,
                placeholder="Select player...",
                )

        submit_button = st.form_submit_button(label='Submit')

    if submit_button:
        st.write(f"The selected player is {selected_player}")

        rendered_pass_map = draw_pass_map(df, selected_player)
        rendered_heat_map = draw_heat_map(df, selected_player)

        if rendered_pass_map:
            st.pyplot(rendered_pass_map)

        if rendered_heat_map:
            st.pyplot(rendered_heat_map)

    return None

st.title("Premier league 24/25 season")

aws_params = st.secrets['aws_params']
s3_client = boto3.client(
        's3',
        **aws_params
        )
bucket_name = "abhishek-data-bucket"

db_params = st.secrets["db_params"]
my_db = FootballDB(db_params)

df_fixtures = load_data("./data/fixtures_2425.csv")
df_home_team = load_data("./data/home_team_data_latest_2425.csv")

teams = sorted(list(team_id_dict.keys()))


with st.form(key="my-form"):
    home_team = st.selectbox(
            "Home team",
            teams,
            index=None,
            placeholder="Select team..."
            )

    away_team = st.selectbox(
            "Away team",
            teams,
            index=None,
            placeholder="Select team..."
            )

    submit_button = st.form_submit_button(label='Submit')

if submit_button:

    st.session_state.confirmed = True

    if home_team == away_team:
        st.write("Choose two distinct teams")

    else:
        game_id = df_fixtures[(df_fixtures["home_team"] == ws_fx_mapping[home_team]) & \
                (df_fixtures["away_team"] == ws_fx_mapping[away_team])]["game_id"].values[0]

        query_string = ws_us_mapping[home_team] + "-" + ws_us_mapping[away_team]

        match_stats_sql = f"""
        SELECT *
        FROM match_stats
        WHERE game LIKE '%{query_string}%'
        """
        event_data_detail_sql = f"""
        SELECT *
        FROM event_data_detail
        WHERE game_id={game_id}
        """

        event_data_spadl_sql = f"""
        SELECT *
        FROM event_data
        WHERE game_id={game_id}
        """

        # df_match_stats = bq_client.query(match_stats_sql).to_dataframe()
        df_match_stats = my_db.read_from_db(match_stats_sql)
        df_game_events_detail = my_db.read_from_db(event_data_detail_sql)
        df_game_events = my_db.read_from_db(event_data_spadl_sql)

        df_game_events = spu.add_names(df_game_events)

        df_game_events = spu.play_left_to_right(df_game_events, team_id_dict[home_team])

        if len(df_game_events) == 0:
            st.write("This game has not been played yet this season")

        else:

            game_file = f"football_data/jsons/{game_id}.json"
            json_data = download_from_s3(s3_client, bucket_name, game_file)

            get_score(json_data['score'], home_team, away_team)

            plot_stats(df_match_stats, home_team, away_team)

            plot_pass_network(df_game_events_detail, json_data, home_team, away_team)

            plot_progressive_passes(df_game_events, home_team)

            plot_progressive_passes(df_game_events, away_team)

            plot_danger_shots(df_game_events, home_team)

            plot_danger_shots(df_game_events, away_team)

            render_player_graphs(df_game_events)
