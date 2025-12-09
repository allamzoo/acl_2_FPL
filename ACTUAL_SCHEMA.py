"""
ACTUAL NEO4J SCHEMA:

Nodes:
- Player: player_name, player_element, embeddings
- Position: name (FWD, MID, DEF, GK)
- Team: name
- Season: season_name (e.g., "2021-22")
- Gameweek: GW_number, season
- Fixture: various properties

Relationships:
- (Player)-[PLAYS_AS]->(Position)
- (Player)-[PLAYED_IN {stats}]->(Gameweek)
- (Gameweek)-[HAS_GW]->(Season)
- Various fixture relationships

PLAYED_IN properties (stats):
- goals_scored, assists, total_points, minutes, bonus, bps
- clean_sheets, goals_conceded, own_goals
- penalties_missed, penalties_saved, red_cards, yellow_cards, saves
- creativity, influence, threat, ict_index, form
- position (FWD/MID/DEF/GK)

Example query for season stats:
MATCH (p:Player)-[played:PLAYED_IN]->(gw:Gameweek)
WHERE gw.season = '2023-24'
WITH p, SUM(played.goals_scored) as total_goals
RETURN p.player_name, total_goals
ORDER BY total_goals DESC
"""
print(__doc__)
