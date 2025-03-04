import streamlit as st
import matplotlib.pyplot as plt
from matplotlib import rcParams

from mplsoccer import Pitch, VerticalPitch, FontManager, Sbopen




def draw_pass_map(df, selected_player):

    # rcParams['text.color'] = '#c7d5cc'

    # pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#c7d5cc')
    pitch = Pitch(pitch_type='custom', pitch_length=105, pitch_width=68)
    fig, ax = pitch.draw(figsize=(16, 11), constrained_layout=False, tight_layout=True)
    # fig.set_facecolor('#22312b')

    pass_df = df[(df["type_name"] == "pass") & (df["player"] == selected_player)]

    lc1 = pitch.lines(pass_df.start_x, pass_df.start_y,
                      pass_df.end_x, pass_df.end_y,
                      lw=5, transparent=True, comet=True, label='Passes',
                      color='#ad993c', ax=ax)

    dribble_df = df[(df["type_name"] == "dribble") & (df["player"] == selected_player)]
    lc2 = pitch.lines(dribble_df.start_x, dribble_df.start_y,
                      dribble_df.end_x, dribble_df.end_y,
                      lw=5, transparent=True, comet=True, label='Dribbles',
                      color='#ba4f45', ax=ax)

    cross_df = df[(df["type_name"] == "cross") & (df["player"] == selected_player)]
    lc3 = pitch.lines(cross_df.start_x, cross_df.start_y,
                     cross_df.end_x, cross_df.end_y,
                     lw=5, transparent=True, comet=True, label='Crosses',
                     color='#6cff2d', ax=ax)

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
