// ==============================================================================
// Query 1: Find Player by Name
// ==============================================================================
// Description: Search for a specific player and get their basic info
// Parameters: $player_name (string)
// Usage: Get player information by name
// Example: player_name = "Mohamed Salah"
// ==============================================================================

MATCH (p:Player)
WHERE p.player_name CONTAINS $player_name
RETURN p.player_name AS name, 
       p.player_element AS id
LIMIT 10;


// ==============================================================================
// Query 2: Top Scorers by Position
// ==============================================================================
// Description: Get top goal scorers for a specific position in a season
// Parameters: $position (string), $season (string), $limit (integer)
// Usage: Find best attacking players by position
// Example: position = "FWD", season = "2021-22", limit = 10
// ==============================================================================

MATCH (p:Player)-[r:PLAYED_IN]->(f:Fixture)
WHERE r.position = $position 
  AND f.season = $season
WITH p.player_name AS player, 
     r.position AS position,
     SUM(r.goals_scored) AS total_goals,
     SUM(r.assists) AS total_assists,
     SUM(r.total_points) AS total_points
ORDER BY total_goals DESC
LIMIT $limit
RETURN player, position, total_goals, total_assists, total_points;


// ==============================================================================
// Query 3: Player Season Statistics
// ==============================================================================
// Description: Get comprehensive statistics for a player in a specific season
// Parameters: $player_name (string), $season (string)
// Usage: Analyze a player's complete season performance
// Example: player_name = "Salah", season = "2021-22"
// ==============================================================================

MATCH (p:Player)-[r:PLAYED_IN]->(f:Fixture)
WHERE p.player_name CONTAINS $player_name 
  AND f.season = $season
RETURN p.player_name AS player,
       f.season AS season,
       COUNT(f) AS games_played,
       SUM(r.minutes) AS total_minutes,
       SUM(r.goals_scored) AS goals,
       SUM(r.assists) AS assists,
       SUM(r.total_points) AS total_points,
       SUM(r.bonus) AS bonus_points,
       SUM(r.clean_sheets) AS clean_sheets,
       SUM(r.yellow_cards) AS yellow_cards,
       SUM(r.red_cards) AS red_cards,
       AVG(r.ict_index) AS avg_ict_index;


// ==============================================================================
// Query 4: Players by Team in Season
// ==============================================================================
// Description: Get all players who played for a specific team in fixtures
// Parameters: $team_name (string), $season (string)
// Usage: Analyze team roster and performance
// Example: team_name = "Liverpool", season = "2021-22"
// ==============================================================================

MATCH (t:Team)<-[:HAS_HOME_TEAM]-(f:Fixture)<-[r:PLAYED_IN]-(p:Player)
WHERE t.name = $team_name 
  AND f.season = $season
WITH DISTINCT p.player_name AS player, 
     r.position AS position,
     SUM(r.total_points) AS total_points
RETURN player, position, total_points
ORDER BY total_points DESC

UNION

MATCH (t:Team)<-[:HAS_AWAY_TEAM]-(f:Fixture)<-[r:PLAYED_IN]-(p:Player)
WHERE t.name = $team_name 
  AND f.season = $season
WITH DISTINCT p.player_name AS player, 
     r.position AS position,
     SUM(r.total_points) AS total_points
RETURN player, position, total_points
ORDER BY total_points DESC;


// ==============================================================================
// Query 5: Gameweek Top Performers
// ==============================================================================
// Description: Find top performers in a specific gameweek
// Parameters: $gameweek (integer), $season (string), $limit (integer)
// Usage: Identify best players in a particular gameweek
// Example: gameweek = 1, season = "2021-22", limit = 10
// ==============================================================================

MATCH (s:Season)-[:HAS_GW]->(gw:Gameweek)-[:HAS_FIXTURE]->(f:Fixture)
MATCH (p:Player)-[r:PLAYED_IN]->(f)
WHERE gw.GW_number = $gameweek 
  AND s.season_name = $season
RETURN p.player_name AS player,
       r.position AS position,
       r.total_points AS points,
       r.goals_scored AS goals,
       r.assists AS assists,
       r.bonus AS bonus,
       r.minutes AS minutes
ORDER BY r.total_points DESC
LIMIT $limit;


// ==============================================================================
// Query 6: Compare Two Players
// ==============================================================================
// Description: Compare statistics between two players in a season
// Parameters: $player1 (string), $player2 (string), $season (string)
// Usage: Head-to-head player comparison
// Example: player1 = "Salah", player2 = "Kane", season = "2021-22"
// ==============================================================================

MATCH (p:Player)-[r:PLAYED_IN]->(f:Fixture)
WHERE (p.player_name CONTAINS $player1 OR p.player_name CONTAINS $player2)
  AND f.season = $season
WITH p.player_name AS player,
     SUM(r.goals_scored) AS goals,
     SUM(r.assists) AS assists,
     SUM(r.total_points) AS total_points,
     SUM(r.minutes) AS minutes,
     AVG(r.ict_index) AS avg_ict,
     COUNT(f) AS games_played
RETURN player, goals, assists, total_points, minutes, avg_ict, games_played
ORDER BY total_points DESC;


// ==============================================================================
// Query 7: High Performers by Threshold
// ==============================================================================
// Description: Find players exceeding specific performance thresholds
// Parameters: $min_goals (integer), $season (string)
// Usage: Filter players by goal-scoring ability
// Example: min_goals = 15, season = "2021-22"
// ==============================================================================

MATCH (p:Player)-[r:PLAYED_IN]->(f:Fixture)
WHERE f.season = $season
WITH p.player_name AS player,
     r.position AS position,
     SUM(r.goals_scored) AS total_goals,
     SUM(r.assists) AS total_assists,
     SUM(r.total_points) AS total_points
WHERE total_goals >= $min_goals
RETURN player, position, total_goals, total_assists, total_points
ORDER BY total_goals DESC;


// ==============================================================================
// Query 8: Best Assisters by Position
// ==============================================================================
// Description: Get top assist providers for a specific position
// Parameters: $position (string), $season (string), $limit (integer)
// Usage: Find best playmakers by position
// Example: position = "MID", season = "2021-22", limit = 10
// ==============================================================================

MATCH (p:Player)-[r:PLAYED_IN]->(f:Fixture)
WHERE r.position = $position 
  AND f.season = $season
WITH p.player_name AS player,
     r.position AS position,
     SUM(r.assists) AS total_assists,
     SUM(r.goals_scored) AS total_goals,
     SUM(r.total_points) AS total_points
ORDER BY total_assists DESC
LIMIT $limit
RETURN player, position, total_assists, total_goals, total_points;


// ==============================================================================
// Query 9: Player Form (Recent Gameweeks)
// ==============================================================================
// Description: Analyze player performance over recent gameweeks
// Parameters: $player_name (string), $season (string), $last_n_gw (integer)
// Usage: Check player's recent form
// Example: player_name = "Salah", season = "2021-22", last_n_gw = 5
// ==============================================================================

MATCH (p:Player)-[r:PLAYED_IN]->(f:Fixture)<-[:HAS_FIXTURE]-(gw:Gameweek)
WHERE p.player_name CONTAINS $player_name 
  AND f.season = $season
WITH p.player_name AS player,
     gw.GW_number AS gameweek,
     r.total_points AS points,
     r.goals_scored AS goals,
     r.assists AS assists,
     r.minutes AS minutes
ORDER BY gameweek DESC
LIMIT $last_n_gw
RETURN player, gameweek, points, goals, assists, minutes
ORDER BY gameweek ASC;


// ==============================================================================
// Query 10: Best Players by ICT Index
// ==============================================================================
// Description: Find players with highest ICT (Influence, Creativity, Threat)
// Parameters: $position (string), $season (string), $limit (integer)
// Usage: Identify most impactful players using FPL's ICT metric
// Example: position = "MID", season = "2021-22", limit = 10
// ==============================================================================

MATCH (p:Player)-[r:PLAYED_IN]->(f:Fixture)
WHERE r.position = $position 
  AND f.season = $season
  AND r.minutes > 0
WITH p.player_name AS player,
     r.position AS position,
     AVG(r.ict_index) AS avg_ict_index,
     AVG(r.influence) AS avg_influence,
     AVG(r.creativity) AS avg_creativity,
     AVG(r.threat) AS avg_threat,
     SUM(r.total_points) AS total_points
ORDER BY avg_ict_index DESC
LIMIT $limit
RETURN player, position, 
       ROUND(avg_ict_index * 10) / 10 AS avg_ict,
       ROUND(avg_influence * 10) / 10 AS avg_influence,
       ROUND(avg_creativity * 10) / 10 AS avg_creativity,
       ROUND(avg_threat * 10) / 10 AS avg_threat,
       total_points;
