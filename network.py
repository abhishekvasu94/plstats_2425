from mplsoccer import Pitch

def process_pass_data(df, match_id, team_name):

    match_data = df[df["match_id"] == match_id]
    match_data = match_data[match_data["team"] == team_name]
    
    subs = match_data[match_data["type"] == "Substitution"]
    subs = subs['minute']
    firstSub = subs.min()
    
    assert firstSub == sorted(subs)[0]
    subs = sorted(set(subs))
    print(subs)

    try:
        secondPhase = subs[1] - subs[0]
    except IndexError:
        secondPhase = 0

    try:
        thirdPhase = subs[2] - subs[1]
    except IndexError:
        thirdPhase = 0
    
    if (subs[0] > secondPhase) & (subs[0] > thirdPhase):
        match_1_pass = match_data[(match_data["type"] == "Pass") & (match_data["minute"] < firstSub)]
    elif secondPhase > thirdPhase:
        match_1_pass = match_data[(match_data["type"] == "Pass") & (match_data["minute"] > firstSub) & (match_data["minute"] < subs[1])]
    else:
        match_1_pass = match_data[(match_data["type"] == "Pass") & (match_data["minute"] > subs[1])]

    successful = match_1_pass[match_1_pass["pass_outcome"].isnull()]
    successful['location'] = successful['location'].apply(literal_eval).apply(np.array)

    average_locations = successful.groupby(['player', 'player_id'])["location"].apply(np.mean).reset_index()
    count_locations = successful.groupby('player')["location"].agg(['count']).reset_index()

    average_locations = average_locations.merge(count_locations, left_on="player", right_on="player")
    avg_loc = pd.DataFrame(average_locations['location'].to_list(), columns = ['x', 'y'])
    average_locations = pd.concat([average_locations, avg_loc], axis=1)

    pass_between = successful.groupby(['player','pass_recipient']).id.count().reset_index()
    pass_between.rename({'id':'pass_count'},axis='columns',inplace=True)
    pass_between= pass_between.merge(average_locations,left_on='player', right_on="player")
    pass_between= pass_between.merge(average_locations,left_on='pass_recipient',right_on="player",suffixes=['','_end'])

    pass_between =pass_between[pass_between['pass_count']>3]

    return pass_between, average_locations


def plot_pass_map(ax, pass_between, average_locations, match_id, df_metadata, team_name):

    pitch = Pitch(pitch_type="custom", pitch_color='#CAD748', line_color='#898C69')
    lineups = sb.lineups(match_id=match_id)[team_name]
    # pitch = Pitch(pitch_type="uefa", line_color='#898C69')
    # Set the figure size
    # fig, ax = pitch.draw(figsize=(8, 6), constrained_layout=True, tight_layout=False)
    pitch.draw(ax=ax)
    
    # Set the face color of the figure
    ax.set_facecolor('#CAD748')
    
    # Draw arrows and nodes
    # arrows = pitch.arrows(1.2 * pass_between.x, 0.8 * pass_between.y, 1.2 * pass_between.x_end, 0.8 * pass_between.y_end, ax=ax,color='red', alpha=0.4,width=3)
    pass_lines = pitch.lines(1.2*pass_between.x, 0.8*pass_between.y, 1.2*pass_between.x_end, 0.8*pass_between.y_end, lw=pass_between.pass_count*0.5,color="#D64E47", zorder=1, ax=ax)
                     
    nodes = pitch.scatter(1.2 * average_locations.x, 0.8 * average_locations.y, s=20*average_locations['count'].values, color='white', edgecolors='#a6aab3', linewidth=2, alpha=1, zorder=1, ax=ax)


    home_team = df_metadata[df_metadata["match_id"] == match_id]["home_team"].values[0]
    away_team = df_metadata[df_metadata["match_id"] == match_id]["away_team"].values[0]
    home_score = df_metadata[df_metadata["match_id"] == match_id]["home_score"].values[0]
    away_score = df_metadata[df_metadata["match_id"] == match_id]["away_score"].values[0]
    competition = df_metadata[df_metadata["match_id"] == match_id]["competition"].values[0]
    season = df_metadata[df_metadata["match_id"] == match_id]["season"].values[0]

    assert len(average_locations) == 11
                     
    # Annotate average_locations
    for index, row in average_locations.iterrows():

        jersey_number = lineups[lineups["player_id"] == row["player_id"]]["jersey_number"].values[0]

        pitch.annotate(jersey_number, xy=(1.2 * row.x, 0.8 * row.y), c='#161A30',fontweight='bold', va='center', ha='center', size=8, ax=ax)
    
    # Add the endnote
    ax.text(105, 84, 'Passing network', color='#485057', va='bottom', ha='center', fontsize=10)
    
    # Add the title
    ax.set_title(f'{home_team} {home_score} - {away_score} {away_team}', color="#011EE6", va='center', ha='center', fontsize=12,fontweight='bold',pad=20,loc='center')
    ax.annotate(f'{competition} {season}', xy=(0.5, 1), xytext=(0, 0),
                 xycoords='axes fraction', textcoords='offset points',
                 fontsize=10, color='#011EE6', va='top', ha='center')
    
    
    # plt.show()
    return ax
