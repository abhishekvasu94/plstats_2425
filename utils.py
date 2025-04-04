import streamlit as st
import matplotlib.pyplot as plt
from matplotlib import rcParams

from mplsoccer import Pitch, VerticalPitch, FontManager, Sbopen




def draw_pass_map(df, selected_player):

    pass_df = df[(df["type_name"] == "pass") & (df["player"] == selected_player)]

    pitch = Pitch(line_color='black', pitch_type = "custom", pitch_length=105, pitch_width=68)
    fig, ax = pitch.draw(figsize=(16, 11), constrained_layout=False, tight_layout=True)

    success_passes = pass_df[pass_df["result_name"] == "success"]
    failed_passes = pass_df[pass_df["result_name"] == "fail"]

    pitch.scatter(pass_df.start_x, pass_df.start_y, alpha = 0.2, s = 50, color = "blue", ax=ax)
    pitch.arrows(success_passes.start_x, success_passes.start_y, success_passes.end_x, success_passes.end_y, label="success", color = "green", ax=ax, width=1)
    pitch.arrows(failed_passes.start_x, failed_passes.start_y, failed_passes.end_x, failed_passes.end_y, label="fail", color = "red", ax=ax, width=1)

    ax.legend(facecolor='#22312b', edgecolor='None', fontsize=20, loc='upper left', handlelength=4)

    ax_title = ax.set_title(f'{selected_player} pass map', fontsize=30)

    st.pyplot(fig)
    return None 

def change_label_style(label, font_size='12px', font_color='black', font_family='sans-serif'):
    html = f"""
    <script>
        var elems = window.parent.document.querySelectorAll('p');
        var elem = Array.from(elems).find(x => x.innerText == '{label}');
        elem.style.fontSize = '{font_size}';
        elem.style.color = '{font_color}';
        elem.style.fontFamily = '{font_family}';
    </script>
    """
    st.components.v1.html(html)
