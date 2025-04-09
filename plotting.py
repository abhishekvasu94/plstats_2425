import json
from mplsoccer import Pitch
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from PIL import Image
import streamlit as st
from config import *
from passes import get_progressive_passes
from network import process_pass_data

def plot_stats(df, home_team, away_team):

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

    return None

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
    fig, ax = pitch_prog_pass.draw(figsize=(16, 11), constrained_layout=False, tight_layout=True)

    pitch_prog_pass.scatter(x_start, y_start, alpha = 0.2, s = 50, color = "blue", ax=ax)
    pitch_prog_pass.arrows(x_start, y_start, x_end, y_end, color = "blue", ax=ax, width=1)
    fig.suptitle("Progressive passes", fontsize=30)

    ax2 = fig.add_axes([0.05,0.88,0.15,0.15]) # badge
    ax2.axis("off")
    img_team = Image.open(team_name_file)
    ax2.imshow(img_team)

    st.pyplot(fig)

    return None

def plot_danger_shots(df, team_name):

    #plot pitch
    pitch = Pitch(line_color='black', pitch_type = "custom", pitch_length=105, pitch_width=68, half=True)
    fig, ax = pitch.grid(grid_height=0.9, title_height=0.06, axis=False,
                         endnote_height=0.04, title_space=0, endnote_space=0)

    danger_shots = df[(df["team"] == team_name) & (df["type_name"].isin(["shot", "shot_penalty", "shot_freekick"]))]

    team_name = team_name.replace(" ", "_")

    team_name_file = f"./data/logos/{team_name}-logo.png"

    fail_shots = danger_shots[danger_shots["result_name"] != "success"]
    success_shots = danger_shots[danger_shots["result_name"] == "success"]

    #scatter the location on the pitch
    pitch.scatter(fail_shots.start_x, fail_shots.start_y, s=100, color='red', edgecolors='grey', linewidth=1, alpha=0.7, ax=ax["pitch"])
    pitch.scatter(success_shots.start_x, success_shots.start_y, s=100, color='green', edgecolors='grey', linewidth=1, alpha=0.7, ax=ax["pitch"])

    #add title
    fig.suptitle('Dangerous shots', fontsize = 30)

    ax2 = fig.add_axes([0.05,0.90,0.15,0.10]) # badge
    ax2.axis("off")
    img_team = Image.open(team_name_file)
    ax2.imshow(img_team)
    st.pyplot(fig)


def plot_pass_network(df, json_data, home_team, away_team):

    home_pass_between, home_avg_locations = process_pass_data(df, json_data, is_home=True)
    away_pass_between, away_avg_location = process_pass_data(df, json_data, is_home=False)

    def plot_pass_map(pass_between, average_locations, players_data, team_name):

        df_players = pd.DataFrame(players_data)

        average_locations["x"] = (average_locations["x"] / 100) * 105
        average_locations["y"] = (average_locations["y"] / 100) * 68

        pass_between["x"] = (pass_between["x"] / 100) * 105
        pass_between["y"] = (pass_between["y"] / 100) * 68
        pass_between["x_end"] = (pass_between["x_end"] / 100) * 105
        pass_between["y_end"] = (pass_between["y_end"] / 100) * 68

        pitch = Pitch(line_color='black', pitch_type = "custom", pitch_length=105, pitch_width=68)
        fig, ax = pitch.draw(figsize=(16, 11), constrained_layout=True, tight_layout=False)
        pitch.draw(ax=ax)
        
        # Draw arrows and nodes
        pass_lines = pitch.lines(1.2*pass_between.x, 0.8*pass_between.y, 1.2*pass_between.x_end, 0.8*pass_between.y_end, lw=pass_between.pass_count*0.5,color="#D64E47", zorder=1, ax=ax)
                        
        nodes = pitch.scatter(1.2 * average_locations.x, 0.8 * average_locations.y, s=20*average_locations['count'].values, color='white', edgecolors='#a6aab3', linewidth=2, alpha=1, zorder=1, ax=ax)

        assert len(average_locations) == 11
                        
        # Annotate average_locations
        for index, row in average_locations.iterrows():

            jersey_numer = df_players[df_players["playerId"] == row.player_id]["shirtNo"].values[0]

            pitch.annotate(jersey_numer, xy=(1.2 * row.x, 0.8 * row.y), c='#161A30',fontweight='bold', va='center', ha='center', size=8, ax=ax)
        
        # Add the endnote
        fig.suptitle("Passing network", fontsize=30)

        team_name = team_name.replace(" ", "_")
        team_file = f"./data/logos/{team_name}-logo.png"

        ax2 = fig.add_axes([0.10,0.85,0.15,0.15]) # badge
        ax2.axis("off")
        img_home = Image.open(team_file)
        ax2.imshow(img_home)

        st.pyplot(fig)
        
        return None

    plot_pass_map(home_pass_between, home_avg_locations, json_data['home']['players'], home_team)
    plot_pass_map(away_pass_between, away_avg_location, json_data['away']['players'], away_team)