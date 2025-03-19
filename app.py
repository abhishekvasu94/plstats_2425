import pandas as pd
import numpy as np
import streamlit as st
from matplotlib import pyplot as plt
import socceraction.spadl.utils as spu
from PIL import Image
from google.oauth2 import service_account
from google.cloud import bigquery

from mplsoccer import VerticalPitch, Pitch

from utils import draw_pass_map, change_label_style
from passes import get_progressive_passes
from shots import plot_danger_shots

team_id_dict = {
        "Arsenal": 13,
        "Man City": 167,
        "Liverpool": 26,
        "Aston Villa": 24,
        "Tottenham": 30,
        "Newcastle": 23,
        "Chelsea": 15,
        "Man Utd": 32,
        "West Ham": 29,
        "Bournemouth": 183,
        "Brighton": 211,
        "Wolves": 161,
        "Fulham": 170,
        "Crystal Palace": 162,
        "Everton": 31,
        "Brentford": 189,
        "Nottingham Forest": 174,
        "Luton": 95,
        "Burnley": 184,
        "Sheff Utd": 163,
        "Leicester": 14,
        "Leeds": 19,
        "Southampton": 18,
        "Ipswich": 165
        }

ws_us_mapping = {
        "Arsenal": "Arsenal",
        "Man City": "Manchester City",
        "Liverpool": "Liverpool",
        "Aston Villa": "Aston Villa",
        "Tottenham": "Tottenham Hotspur",
        "Newcastle": "Newcastle United",
        "Chelsea": "Chelsea",
        "Man Utd": "Manchester United",
        "West Ham": "West Ham United",
        "Bournemouth": "AFC Bournemouth",
        "Brighton": "Brighton & Hove Albion",
        "Wolves": "Wolverhampton Wanderers",
        "Fulham": "Fulham",
        "Crystal Palace": "Crystal Palace",
        "Everton": "Everton",
        "Brentford": "Brentford",
        "Nottingham Forest": "Nottingham Forest",
        "Leicester": "Leicester City",
        "Southampton": "Southampton",
        "Ipswich": "Ipswich Town"
        }

ws_fx_mapping = {
        "Arsenal": "Arsenal",
        "Man City": "Manchester City",
        "Liverpool": "Liverpool",
        "Aston Villa": "Aston Villa",
        "Tottenham": "Tottenham",
        "Newcastle": "Newcastle",
        "Chelsea": "Chelsea",
        "Man Utd": "Manchester United",
        "West Ham": "West Ham",
        "Bournemouth": "Bournemouth",
        "Brighton": "Brighton",
        "Wolves": "Wolves",
        "Fulham": "Fulham",
        "Crystal Palace": "Crystal Palace",
        "Everton": "Everton",
        "Brentford": "Brentford",
        "Nottingham Forest": "Nottingham Forest",
        "Leicester": "Leicester",
        "Southampton": "Southampton",
        "Ipswich": "Ipswich"
        }

@st.cache_data
def load_data(filename):
    return pd.read_csv(filename)

def plot_stats(df, home_team, away_team):

    # columns = ['Ball possession', 'Big chances', 'Big chances missed', 'Corners', 'Expected goals (xG)', 'Fouls committed', 'Shots on target', 'Total shots', 'Accurate passes (%)']
    columns = ['ball_possession', 'big_chances', 'big_chances_missed', 'corners', 'expected_goals', 'fouls_committed', 'shots_on_target', 'total_shots','accurate_passes_percentage']

    home_df = df[df["team"] == ws_us_mapping[home_team]]
    away_df = df[df["team"] == ws_us_mapping[away_team]]

    home_team = home_team.replace(" ", "_")
    away_team = away_team.replace(" ", "_")

    home_team_file = f"./data/logos/{home_team}-logo.png"
    away_team_file = f"./data/logos/{away_team}-logo.png"

    fig = plt.figure(figsize=(8,8), dpi=300)
    ax = plt.subplot()
    ax.set_axis_off()

    for idx, col in enumerate(columns):
        
        val_1 = home_df[col].values[0]
        val_2 = away_df[col].values[0]

        if 'percentage' in col:
            val_1 *= 100
            val_2 *= 100

        first_val = val_1 / (val_1 + val_2)
        second_val = val_2 / (val_1 + val_2)

        field_name = col.replace("_", " ").replace("percentage", "(%)").capitalize()

        ax.text(0.5, idx * 2 + 0.8, field_name, ha='center', weight="bold", color='#9836EB')
        ax.barh(idx * 2, first_val, color='red', label='Team 1', alpha=0.5)
        if val_1 != 0:
            ax.text(first_val / 2, idx * 2 - 0.15, str(round(val_1, 2)), weight="bold", ha='center', color="#967D54")
        ax.barh(idx * 2, second_val, left=first_val, color='grey', label='Team 2', alpha=0.5)
        if val_2 != 0:
            ax.text(first_val + second_val / 2, idx * 2 - 0.15, str(round(val_2, 2)), weight="bold", ha='center', color='#967D54')

    ax2 = fig.add_axes([0.10,0.85,0.15,0.15]) # badge
    ax2.axis("off")
    img_home = Image.open(home_team_file)
    ax2.imshow(img_home)

    ax3 = fig.add_axes([0.75,0.85,0.15,0.15]) # badge
    ax3.axis("off")
    img_away = Image.open(away_team_file)
    ax3.imshow(img_away)


    st.pyplot(fig)

def plot_progressive_passes(df, team_name, is_away_team=False):

    new_df = df.copy()


    if is_away_team:
        new_df["start_x"] = 105 - new_df["start_x"]
        new_df["end_x"] = 105 - new_df["end_x"]
        new_df["start_y"] = 68 - new_df["start_y"]
        new_df["end_y"] = 68 - new_df["end_y"]

    df_progressive = get_progressive_passes(new_df, team_name)

    x_start = df_progressive["start_x"]
    x_end = df_progressive["end_x"]
    y_start = df_progressive["start_y"]
    y_end = df_progressive["end_y"]

    team_name = team_name.replace(" ", "_")

    team_name_file = f"./data/logos/{team_name}-logo.png"

    pitch_prog_pass = Pitch(line_color='black', pitch_type = "custom", pitch_length=105, pitch_width=68)
    fig, ax = pitch_prog_pass.draw()

    pitch_prog_pass.scatter(x_start, y_start, alpha = 0.2, s = 50, color = "blue", ax=ax)
    pitch_prog_pass.arrows(x_start, y_start, x_end, y_end, color = "blue", ax=ax, width=1)
    fig.suptitle("Progressive passes", fontsize=30)

    ax2 = fig.add_axes([0.05,0.88,0.15,0.15]) # badge
    ax2.axis("off")
    img_team = Image.open(team_name_file)
    ax2.imshow(img_team)

    st.pyplot(fig)


def get_score(df_events, home_team, away_team):

    goals_df = df_events[(df_events["type_name"].isin(["shot", "shot_penalty", "shot_freekick"])) & (df_events["result_name"] == "success")]

    owngoals_df = df_events[df_events["result_name"] == "owngoal"]

    home_goals = len(goals_df[goals_df["team"] == home_team]) + len(owngoals_df[owngoals_df["team"] == away_team])
    away_goals = len(goals_df[goals_df["team"] == away_team]) + len(owngoals_df[owngoals_df["team"] == home_team])

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

        rendered_fig = draw_pass_map(df, selected_player)
        if rendered_fig:
            st.pyplot(rendered_fig)

    return None

st.title("Premier league 24/25 season")

# Create API client.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

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
            FROM `match_stats.match_stats`
            WHERE game LIKE '%{query_string}%'
        """
        df_match_stats = client.query(match_stats_sql).to_dataframe()

        event_data_sql = f"""
            SELECT *
            FROM `events_data.event_data`
            WHERE game_id={game_id}
        """
        df_game_events = client.query(event_data_sql).to_dataframe()
        df_game_events = spu.add_names(df_game_events)

        df_game_events = spu.play_left_to_right(df_game_events, team_id_dict[home_team])

        if len(df_game_events) == 0:
            st.write("This game has not been played yet this season")

        else:

            get_score(df_game_events, home_team, away_team)

            plot_stats(df_match_stats, home_team, away_team)

            plot_progressive_passes(df_game_events, home_team)

            plot_progressive_passes(df_game_events, away_team)

            plot_danger_shots(df_game_events, home_team)

            plot_danger_shots(df_game_events, away_team)

            render_player_graphs(df_game_events)

