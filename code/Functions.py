###########################################################
# The functions used in the main program are defined here.
# Last Updated: 6.12.2024
###########################################################

# Importing the necessary libraries
import requests
import os
import json
import time
import re
from dotenv import load_dotenv

###########################################################
# Function: get_spotify_token
def get_spotify_token(client_id, client_secret):
    """
    A function that authenticates with Spotify API and get an access token.

    Params:
        client_id (str): Spotify API client ID.
        client_secret (str): Spotify API client secret.

    Returns:
        str: Spotify API access token.
    """
    url = "https://accounts.spotify.com/api/token"
    data = {"grant_type": "client_credentials"}
    response = requests.post(url, data=data, auth=(client_id, client_secret))
    response.raise_for_status()
    return response.json()["access_token"]

###########################################################
# Function: get_spotify_playlist

def search_playlists(query, token, limit=10, min_tracks=10, min_followers=50):
    """
    A function to search for playlists using the Spotify API with more flexible searching

    Params:
        query (str): Search keyword (e.g., "morning", "night").
        token (str): Spotify API access token.
        limit (int): Number of playlists to retrieve (default 10).
        min_tracks (int): Minimum number of tracks a playlist must have (default 10)
        min_followers (int): Minimum number of followers a playlist must have (default 50)

    Returns:
        list: Sorted list of playlist IDs by followers.
    """
    time_periods = ["morning", "afternoon", "evening", "night"]
    excluded_terms = [term for term in time_periods if term.lower() != query.lower()]

    # Construct more flexible search queries
    search_variations = [
        f"{query} playlist",
        f"*{query}*",
        f"{query} music",
        f"{query} vibes"
    ]

    valid_playlists = []
    seen_playlist_ids = set() # to prevent duplicates

    for search_query in search_variations:
        url = "https://api.spotify.com/v1/search"
        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "q": search_query, 
            "type": "playlist", 
            "limit": limit
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        playlists = response.json()
        if "playlists" not in playlists or "items" not in playlists["playlists"]:
            continue
    
        for playlist in playlists["playlists"]["items"]:
            try:
                # Skip if playlist is None
                if not playlist:
                    continue

                # Check for required fields
                if "name" not in playlist or "tracks" not in playlist:
                    continue

                # Filter out Spotify-generated playlists
                if playlist.get("owner", {}).get("id") == "spotify":
                    continue

                # Check if title contains any excluded terms
                if any(re.search(rf'\b{term}\b', playlist["name"], re.IGNORECASE) for term in excluded_terms):
                    continue
                
                # Check minimum track count
                if playlist["tracks"].get("total", 0) < min_tracks:
                    continue

                # To remove artist tour setlists
                if "setlist" in playlist.get("name", "").lower():
                    continue

                # Fetch additional details for followers
                playlist_id = playlist["id"]
                if playlist_id in seen_playlist_ids:  # Skip duplicates
                    continue

                details = get_playlist_details(playlist_id, token)
                if details and "followers" in details:
                    followers = details["followers"]["total"]
                    if followers < min_followers:
                        continue
                    playlist["followers"] = followers
                    valid_playlists.append(playlist)
                    seen_playlist_ids.add(playlist_id)

            except Exception as e:
                print(f"Error processing playlist: {str(e)}")

    # Sort playlists by followers
    sorted_playlists = sorted(valid_playlists, key=lambda x: x["followers"], reverse=True)

    # Debugging: Print sorted playlists
    print("Filtered and Sorted Playlists:")
    for playlist in sorted_playlists:
        print(f"{playlist['name']} - Followers: {playlist.get('followers', 0)} - Tracks: {playlist['tracks']['total']}")

    # Return only playlist IDs
    playlist_ids = [playlist["id"] for playlist in sorted_playlists]
    return playlist_ids

def get_playlist_details(playlist_id, token):
    """
    Get detailed metadata for a Spotify playlist (including followers).

    Args:
        playlist_id (str): Spotify playlist ID.
        token (str): Spotify API access token.

    Returns:
        dict: Detailed playlist metadata.
    """
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching details for playlist {playlist_id}: {response.status_code}")
        return None

###########################################################
# Function: get_playlist_tracks
def get_playlist_tracks(playlist_id, token):
    """
    A function to get tracks from a Spotify playlist.

    Params:
        playlist_id (str): Spotify playlist ID.
        token (str): Spotify API access token.

    Returns:
        dict: JSON response with playlist tracks.
    """
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

###########################################################

def get_track_genres(playlist_id, token):
    """
    Fetch genres for the first 200 tracks of a playlist using batched artist requests.

    Params:
        playlist_id (str): The ID of the playlist.
        token (str): The Spotify API access token.

    Returns:
        dict: A dictionary mapping track names to artist genres.
    """
    playlist_tracks = get_playlist_tracks(playlist_id, token)
    if not playlist_tracks or "items" not in playlist_tracks:
        print(f"No tracks found for playlist ID: {playlist_id}")
        return {}

    genres = {}
    artist_ids = []  # Collect all artist IDs from the playlist

    for item in playlist_tracks["items"][:200]:  # Limit to 200 tracks
        track = item.get("track")
        if not track:
            continue

        track_name = track.get("name")
        track_artists = [
            {"name": artist["name"], "id": artist["id"], "track": track_name}
            for artist in track.get("artists", [])
            if "id" in artist
        ]
        artist_ids.extend(track_artists)  # Collect artists with associated track names

    # Batch artist IDs into groups of 50
    for i in range(0, len(artist_ids), 50):
        batch = artist_ids[i:i + 50]
        artist_id_str = ",".join([artist["id"] for artist in batch if artist["id"]])
        url = "https://api.spotify.com/v1/artists"
        headers = {"Authorization": f"Bearer {token}"}
        params = {"ids": artist_id_str}

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 429:  # Handle rate-limiting
            retry_after = int(response.headers.get("Retry-After", 60))
            print(f"Rate limit hit. Retrying after {retry_after} seconds...")
            time.sleep(retry_after)
            continue
        
        if response.status_code == 200:
            data = response.json()["artists"]
            for artist in data:
                if artist is None:  # Check if artist is None before accessing its attributes
                    print("Warning: Found NoneType artist in the response")
                    continue

                artist_name = artist.get("name", "Unknown Artist")
                artist_genres = artist.get("genres", [])
                for artist_info in batch:
                    if artist_info["id"] == artist.get("id"):  # Use .get() to avoid KeyError
                        genres[artist_info["track"]] = artist_genres
    
    return genres

###########################################################
# Function: save_json
def save_json(data, filename, folder=None):
    """
    A function to save JSON data to a file.

    Paramss:
        data (dict): JSON data to save.
        filename (str): Name of the file (without extension).
        folder (str): Folder path to save the file
    """
    if folder is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        folder = os.path.join(base_dir, "data/raw")
    
    # Ensure the directory exists
    os.makedirs(folder, exist_ok=True)

    # Save the JSON file
    with open(f"{folder}/{filename}.json", "w") as f:
        json.dump(data, f, indent=4)

###########################################################

######################################################################################################################################
#                                                                Testing
######################################################################################################################################

def main() -> None:

    ######################################################################################################################################

    # Load environment variables
    load_dotenv()
    SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        print("Client ID or Secret not found in environment variables")

    ######################################################################################################################################

    # Testing get_spotify_token function
    try:
        print("Testing get_spotify_token...")
        token = get_spotify_token(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
        print(f"Access Token: {token}")
    except Exception as e:
        print(f"Error in get_spotify_token: {e}")

    print("\n")

    ######################################################################################################################################

    # Testing search_playlists function
    playlists = search_playlists("morning", token, limit=20, min_tracks=10)

    if playlists:
        print("Valid Playlists:")
        for playlist in playlists:
            print(playlist)
    else:
        print("No valid playlists found.")

    playlists = search_playlists("evening", token, limit=20, min_tracks=10)

    if playlists:
        print("Valid Playlists:")
        for playlist in playlists:
            print(playlist)
    else:
        print("No valid playlists found.")

    print("\n")

    ######################################################################################################################################

    # Testing get_playlist_tracks function
    playlist_id = "4OrLCnci10VO8DlSQ7VK5d" # the first playlist from the search results
    tracks = get_playlist_tracks(playlist_id, token)

    if tracks:
        print("Playlist Tracks:")
        for track in tracks["items"]:
            # Access track details, including name, artist, and ID
            track_name = track["track"]["name"]
            artist_name = track["track"]["artists"][0]["name"]
            track_id = track["track"]["id"]
            print(f"{track_name} - {artist_name} (ID: {track_id})")
    else:
        print("No tracks found for the playlist.")
    
    print("\n")

    ######################################################################################################################################

    # Testing get_track_genres function
    track_genres = get_track_genres(playlist_id, token)

    if track_genres:
        print("Track Genres:")
        for track, genres in track_genres.items():
            print(f"{track}: {genres}")
    else:
        print("No genres found for the tracks.")

    print("\n")

    playlist_id = "6X7wz4cCUBR6p68mzM7mZ4"
    track_genres = get_track_genres(playlist_id, token)

    if track_genres:
        print("Track Genres:")
        for track, genres in track_genres.items():
            print(f"{track}: {genres}")
    else:
        print("No genres found for the tracks.")

    ######################################################################################################################################

if __name__ == "__main__":
    main()