"""
Player Photos Module

Handles fetching player photos from FPL API and historical archives.
"""

import streamlit as st
import requests
import pandas as pd
import logging
import re

logger = logging.getLogger(__name__)


@st.cache_data(ttl=3600)
def get_fpl_players():
    """Fetch current season player data from FPL API."""
    try:
        url = "https://fantasy.premierleague.com/api/bootstrap-static/"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        players = []
        for element in data.get('elements', []):
            player = {
                'first_name': element.get('first_name', ''),
                'second_name': element.get('second_name', ''),
                'web_name': element.get('web_name', ''),
                'code': element.get('code', 0)
            }
            players.append(player)
        
        logger.info(f"✓ Loaded {len(players)} players from FPL API")
        return players
    except Exception as e:
        logger.error(f"✗ Error fetching FPL players: {e}")
        return []


def get_fpl_players_from_archive(season_year):
    """Fetch players from FPL archive (https://github.com/vaastav/Fantasy-Premier-League)."""
    try:
        season_str = f"{season_year}-{str(season_year + 1)[-2:]}"
        url = f"https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/{season_str}/players_raw.csv"
        logger.info(f"📥 Attempting to fetch archive: {url}")
        
        try:
            df = pd.read_csv(url)
            logger.info(f"✓ Loaded CSV with {len(df)} rows from {season_str}")
            
            players = []
            for _, row in df.iterrows():
                try:
                    code_val = row.get('code', 0)
                    if pd.notna(code_val):
                        code = int(code_val)
                        if code > 0:
                            player = {
                                'first_name': str(row.get('first_name', '')),
                                'second_name': str(row.get('second_name', '')),
                                'web_name': str(row.get('web_name', '')),
                                'code': code
                            }
                            players.append(player)
                except (ValueError, TypeError):
                    continue
            
            logger.info(f"✓ Processed {len(players)} valid players from {season_str} archive")
            return players
        except Exception as e:
            logger.warning(f"✗ Failed to load archive for {season_str}: {type(e).__name__}: {e}")
            return []
    except Exception as e:
        logger.error(f"✗ Error in get_fpl_players_from_archive for {season_year}: {e}")
        return []


def find_player_in_fpl_data(player_name, players_list):
    """Search for a player in a given FPL players list."""
    search_name = ' '.join(player_name.lower().strip().split())
    search_parts = search_name.split()
    
    best_match = None
    best_score = 0
    
    for player in players_list:
        fpl_first = player.get('first_name', '').lower().strip()
        fpl_second = player.get('second_name', '').lower().strip()
        fpl_web = player.get('web_name', '').lower().strip()
        fpl_full = f"{fpl_first} {fpl_second}".strip()
        
        score = 0
        
        # Exact matches (highest priority)
        if search_name == fpl_full:
            score = 100
        elif search_name == fpl_web:
            score = 95
        elif search_name == fpl_second:
            score = 90
        # Last name exact match
        elif len(search_parts) >= 2 and search_parts[-1] == fpl_second:
            score = 85
        # Full name contains search
        elif search_name in fpl_full:
            score = 70
        # Last name in search
        elif len(search_parts) >= 2 and search_parts[-1] in fpl_second:
            score = 60
        # Web name contains search
        elif search_name in fpl_web:
            score = 55
        
        if score > best_score:
            best_score = score
            best_match = player
    
    return best_match, best_score


def find_player_photo(player_name):
    """Find player photo URL from FPL API, searching current and historical seasons."""
    try:
        # First, try current season
        current_players = get_fpl_players()
        best_match, best_score = find_player_in_fpl_data(player_name, current_players)
        
        # If we have a good match in current season (score >= 60)
        if best_match and best_score >= 60:
            player_code = best_match.get('code')
            if player_code and player_code > 0:
                photo_url = f"https://resources.premierleague.com/premierleague/photos/players/110x140/p{player_code}.png"
                
                # Verify the photo exists
                try:
                    response = requests.head(photo_url, timeout=2)
                    if response.status_code == 200:
                        logger.info(f"✓ Found photo for '{player_name}' in current season (code: {player_code})")
                        return photo_url
                except Exception as e:
                    logger.debug(f"Photo verification failed for code {player_code}: {e}")
        
        # If not found in current season, try historical seasons from GitHub archive
        logger.info(f"🔍 '{player_name}' not in current season (score: {best_score}), searching archives...")
        
        # Go back through recent seasons
        seasons_to_try = [
            (2023, "2023-24"),
            (2022, "2022-23"),
            (2021, "2021-22"),
            (2020, "2020-21"),
            (2019, "2019-20"),
            (2018, "2018-19"),
        ]
        
        for season_year, season_str in seasons_to_try:
            try:
                logger.debug(f"  📅 Checking {season_str}...")
                
                historical_players = get_fpl_players_from_archive(season_year)
                if not historical_players:
                    logger.debug(f"  ⚠️ No data retrieved for {season_str}")
                    continue
                
                logger.debug(f"  ✓ Got {len(historical_players)} players from {season_str}")
                hist_match, hist_score = find_player_in_fpl_data(player_name, historical_players)
                
                if hist_match and hist_score >= 60:
                    player_code = hist_match.get('code')
                    if player_code and player_code > 0:
                        logger.info(f"  🎯 MATCH: {hist_match.get('web_name')} in {season_str} (code: {player_code}, score: {hist_score})")
                        
                        # Try multiple photo formats
                        photo_urls_to_try = [
                            f"https://resources.premierleague.com/premierleague/photos/players/110x140/p{player_code}.png",
                            f"https://resources.premierleague.com/premierleague/photos/players/250x250/p{player_code}.png",
                            f"https://resources.premierleague.com/premierleague/photos/players/40x40/p{player_code}.png",
                        ]
                        
                        for photo_url in photo_urls_to_try:
                            try:
                                logger.debug(f"    Testing: {photo_url}")
                                response = requests.head(photo_url, timeout=2)
                                if response.status_code == 200:
                                    logger.info(f"  ✅ PHOTO FOUND at {photo_url}")
                                    # Always return 110x140 size
                                    return f"https://resources.premierleague.com/premierleague/photos/players/110x140/p{player_code}.png"
                                else:
                                    logger.debug(f"    ✗ Status {response.status_code}")
                            except Exception as e:
                                logger.debug(f"    ✗ Request failed: {e}")
                                continue
                    else:
                        logger.debug(f"  ⚠️ Match found but invalid code: {player_code}")
                else:
                    logger.debug(f"  ✗ No good match in {season_str} (score: {hist_score})")
            except Exception as e:
                logger.debug(f"  Error searching {season_str}: {e}")
                continue
        
        # Player not found in any season, use alternative
        logger.info(f"✗ Player '{player_name}' not found in any season, using avatar")
        return find_player_photo_alternative(player_name)
        
    except Exception as e:
        logger.error(f"Error finding player photo for '{player_name}': {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return find_player_photo_alternative(player_name)


def find_player_photo_alternative(player_name):
    """Generate an avatar URL for player without photo."""
    initials = get_player_initials(player_name)
    return f"https://ui-avatars.com/api/?name={initials}&size=140&background=37003c&color=00ff87&bold=true&font-size=0.4&rounded=true"


def get_player_initials(player_name):
    """Extract initials from player name."""
    parts = player_name.split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[-1][0]}"
    elif len(parts) == 1:
        return parts[0][:2].upper()
    return "??"


def extract_player_names_from_response(response_text):
    """Extract player names from LLM response text."""
    import re
    
    logger.info(f"📄 Response text to parse:\n{response_text[:500]}...")
    
    mentioned_names = []
    
    # Multiple extraction strategies
    # Strategy 1: Match capitalized names (2-4 words)
    pattern1 = r'\b([A-Z][a-z]+(?:\s+(?:van|de|De|Van|der|Der|den|Den)\s+)?(?:[A-Z][a-z]+)+)\b'
    matches1 = re.findall(pattern1, response_text)
    
    # Strategy 2: Match names in bullet points or numbered lists
    pattern2 = r'(?:^|\n)(?:[\*\•\-]|\d+\.)\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)'
    matches2 = re.findall(pattern2, response_text, re.MULTILINE)
    
    # Strategy 3: Match names followed by position indicator
    pattern3 = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s*\([A-Z]{3}\)'
    matches3 = re.findall(pattern3, response_text)
    
    # Strategy 4: Match names before common verbs/words
    pattern4 = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s+(?:scored|has|is|with|had|made|provided|kept|recorded)'
    matches4 = re.findall(pattern4, response_text)
    
    # Combine all matches
    all_matches = matches1 + matches2 + matches3 + matches4
    
    logger.info(f"🔍 Pattern matches: strategy1={len(matches1)}, strategy2={len(matches2)}, strategy3={len(matches3)}, strategy4={len(matches4)}")
    
    # Filter and clean names
    for name in all_matches:
        name = name.strip()
        parts = name.split()
        # Keep names with 2-4 words and reasonable length
        if 2 <= len(parts) <= 4 and 5 <= len(name) <= 40:
            # Exclude common false positives
            if name not in ['Premier League', 'Fantasy Premier', 'Total Points', 'Clean Sheets', 
                           'These Statistics', 'Fantasy Football', 'Support This']:
                if name not in mentioned_names:  # Avoid duplicates
                    mentioned_names.append(name)
    
    logger.info(f"📝 Extracted {len(mentioned_names)} player names: {mentioned_names}")
    return mentioned_names
