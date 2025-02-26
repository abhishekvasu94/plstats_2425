import numpy as np
import streamlit as st
from mplsoccer import Pitch
from PIL import Image

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
    #uncomment it to plot arrows
    #pitch.arrows(danger_passes.x, danger_passes.y, danger_passes.end_x, danger_passes.end_y, color = "blue", ax=ax['pitch'])
    #add title
    fig.suptitle('Dangerous shots', fontsize = 30)

    ax2 = fig.add_axes([0.05,0.90,0.15,0.10]) # badge
    ax2.axis("off")
    img_team = Image.open(team_name_file)
    ax2.imshow(img_team)
    st.pyplot(fig)
