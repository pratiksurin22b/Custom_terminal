import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
from datetime import datetime
import os
from difflib import get_close_matches

from utilities import log_output

class SpotifyController:
    def __init__(self):
        # Replace with your Spotify API credentials
        self.CLIENT_ID = os.environ['spotify_client_id']
        self.CLIENT_SECRET = os.environ['spotify_client_secret']
        self.REDIRECT_URI = "http://localhost:8888/callback"
        self.SCOPE = (
            "user-read-playback-state user-modify-playback-state user-read-currently-playing "
            "playlist-read-private user-library-read streaming user-read-recently-played "
            "playlist-modify-public playlist-modify-private user-library-modify app-remote-control"
        )

        
        try:
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=self.CLIENT_ID,
                client_secret=self.CLIENT_SECRET,
                redirect_uri=self.REDIRECT_URI,
                scope=self.SCOPE
            ))
            self.is_connected = True
        except Exception as e:
            self.is_connected = False
            print(f"Failed to initialize Spotify: {e}")

    def search_and_play(self, query, text_area):
        """Search for a track and play it"""
        try:
            # Search for the track
            results = self.sp.search(q=query, limit=5, type='track')
            
            if not results['tracks']['items']:
                log_output(text_area, f"No results found for '{query}'")
                return
            
            # Display search results
            log_output(text_area, "\nSearch Results:")
            for i, track in enumerate(results['tracks']['items'], 1):
                artists = ", ".join([artist['name'] for artist in track['artists']])
                log_output(text_area, f"{i}. {track['name']} - {artists}")
            
            # Play the first result
            track_uri = results['tracks']['items'][0]['uri']
            self.sp.start_playback(uris=[track_uri])
            
            track = results['tracks']['items'][0]
            artists = ", ".join([artist['name'] for artist in track['artists']])
            log_output(text_area, f"\nNow playing: {track['name']} by {artists}")
            
        except Exception as e:
            log_output(text_area, f"Error: {e}")

    def play_pause(self, text_area):
        """Toggle play/pause"""
        try:
            playback = self.sp.current_playback()
            if playback:
                if playback['is_playing']:
                    self.sp.pause_playback()
                    log_output(text_area, "Playback paused")
                else:
                    self.sp.start_playback()
                    log_output(text_area, "Playback resumed")
        except Exception as e:
            log_output(text_area, f"Error: {e}")

    def next_track(self, text_area):
        """Play next track"""
        try:
            self.sp.next_track()
            # Wait briefly for track to change
            import time
            time.sleep(0.5)
            current = self.sp.current_playback()
            if current and current['item']:
                track = current['item']
                artists = ", ".join([artist['name'] for artist in track['artists']])
                log_output(text_area, f"Now playing: {track['name']} by {artists}")
        except Exception as e:
            log_output(text_area, f"Error: {e}")

    def previous_track(self, text_area):
        """Play previous track"""
        try:
            self.sp.previous_track()
            # Wait briefly for track to change
            import time
            time.sleep(0.5)
            current = self.sp.current_playback()
            if current and current['item']:
                track = current['item']
                artists = ", ".join([artist['name'] for artist in track['artists']])
                log_output(text_area, f"Now playing: {track['name']} by {artists}")
        except Exception as e:
            log_output(text_area, f"Error: {e}")

    def toggle_shuffle(self, text_area):
        """Toggle shuffle mode"""
        try:
            playback = self.sp.current_playback()
            if playback:
                new_state = not playback['shuffle_state']
                self.sp.shuffle(new_state)
                log_output(text_area, f"Shuffle {'enabled' if new_state else 'disabled'}")
        except Exception as e:
            log_output(text_area, f"Error: {e}")

    def get_current_track(self, text_area):
        """Helper method to get current track with retry and better error handling"""
        try:
            current = self.sp.current_playback()
            
            # Check if there's no active device
            if current is None:
                log_output(text_area, "No active Spotify device found. Please start Spotify on any device.")
                return None
                
            # Check if there's no active track
            if not current.get('item'):
                log_output(text_area, "No track is currently playing. Please start playing a track.")
                return None
            
            track = current['item']
            track_name = track['name']
            track_uri = track['uri']
            track_artists = ", ".join([artist['name'] for artist in track['artists']])  # List of artists
            track_album = track['album']['name']
            track_duration = track['duration_ms'] / 1000  # Duration in seconds
            
            # Log the current track details
            log_output(text_area, f"\nCurrently playing track: '{track_name}'")
            log_output(text_area, f"Artist(s): {track_artists}")
            log_output(text_area, f"Album: {track_album}")
            log_output(text_area, f"Track URI: {track_uri}")
            log_output(text_area, f"Duration: {int(track_duration)} seconds")
            
            return current
        
            
        except Exception as e:
            log_output(text_area, f"Error getting current playback state: {str(e)}")
            return None


    def set_volume(self, volume_percent, text_area):
        """Set volume (0-100)"""
        try:
            volume = max(0, min(100, int(volume_percent)))
            self.sp.volume(volume)
            log_output(text_area, f"Volume set to {volume}%")
        except Exception as e:
            log_output(text_area, f"Error setting volume: {e}")

    def list_playlists(self, text_area):
        """List user's playlists"""
        try:
            playlists = self.sp.current_user_playlists()
            if not playlists['items']:
                log_output(text_area, "No playlists found")
                return
                
            log_output(text_area, "\nYour Playlists:")
            for i, playlist in enumerate(playlists['items'], 1):
                track_count = playlist['tracks']['total']
                log_output(text_area, f"{i}. {playlist['name']} ({track_count} tracks)")
        except Exception as e:
            log_output(text_area, f"Error listing playlists: {e}")
        
    def get_playlist_id_by_name(self, playlist_name, text_area):
        """Get the playlist ID by name."""
        try:
            playlists = self.sp.current_user_playlists()
            playlist_name_lower = playlist_name.lower()
            playlist_names = [p['name'].lower() for p in playlists['items']]
            
            # Find the closest match
            match = get_close_matches(playlist_name_lower, playlist_names, n=1, cutoff=0.8)
            if not match:
                log_output(text_area, "The playlist does not match any of the available playlists")
                return None
            
            # Find the matching playlist object
            playlist = next((p for p in playlists['items'] if p['name'].lower() == match[0]), None)
            if not playlist:
                log_output(text_area, "The playlist does not match any of the available playlists")
                return None
            
            log_output(text_area, f"The playlist name is {playlist['name']}")
            return playlist['id']
        except Exception as e:
            log_output(text_area, f"Error while retrieving playlist ID: {str(e)}")
            return None


    def play_playlist(self, playlist_name, text_area):
        """Play a specific playlist"""
        try:
            playlists = self.sp.current_user_playlists()
            playlist = next((p for p in playlists['items'] if p['name'].lower() == playlist_name.lower()), None)
            
            if playlist:
                self.sp.start_playback(context_uri=playlist['uri'])
                log_output(text_area, f"Playing playlist: {playlist['name']}")
            else:
                log_output(text_area, f"Playlist '{playlist_name}' not found")
        except Exception as e:
            log_output(text_area, f"Error playing playlist: {e}")

    def create_playlist(self, name, text_area):
        """Create a new playlist"""
        try:
            user_id = self.sp.current_user()['id']
            playlist = self.sp.user_playlist_create(user_id, name)
            log_output(text_area, f"Created playlist: {name}")
        except Exception as e:
            log_output(text_area, f"Error creating playlist: {e}")

    def add_current_playing_to_playlist(self, playlist_name, text_area):
        """Adding the currently playing track into a playlist with enhanced error handling."""
        try:
            # Log the input parameters for better traceability
            log_output(text_area, f"Attempting to add current playing track to playlist: {playlist_name}")
            
            # Get playlist ID by name
            playlist_id = self.get_playlist_id_by_name(playlist_name, text_area)
            if not playlist_id:
                log_output(text_area, f"Playlist '{playlist_name}' not found.")
                return
            
            # Get the currently playing track with enhanced error handling
            current = self.get_current_track(text_area)
            if not current:
                return
                
            track = current['item']
            track_uri = track['uri']
            track_name = track['name']
            
            # Log track details
            log_output(text_area, f"Currently playing track: {track_name} (URI: {track_uri})")
            
            # Add track to the playlist
            self.sp.playlist_add_items(playlist_id, [track_uri], position=None)
            
            # Log success
            log_output(text_area, f"Successfully added '{track_name}' to the playlist '{playlist_name}'.")
        
        except Exception as e:
            # Log detailed error information
            log_output(text_area, f"Error occurred while adding track to playlist '{playlist_name}': {str(e)}")

        
    def get_recommendations(self, text_area):
        """Get song recommendations based on recent plays"""
        try:
            # Get recently played tracks
            recent = self.sp.current_user_recently_played(limit=5)
            if not recent['items']:
                log_output(text_area, "No recent tracks found for recommendations")
                return
                
            # Get track IDs for seed
            seed_tracks = [item['track']['id'] for item in recent['items'][:2]]
            
            # Get recommendations
            recommendations = self.sp.recommendations(seed_tracks=seed_tracks, limit=5)
            
            log_output(text_area, "\nRecommended Tracks:")
            for i, track in enumerate(recommendations['tracks'], 1):
                artists = ", ".join([artist['name'] for artist in track['artists']])
                log_output(text_area, f"{i}. {track['name']} - {artists}")
        except Exception as e:
            log_output(text_area, f"Error getting recommendations: {e}")

    def view_queue(self, text_area):
        """View current playback queue"""
        try:
            queue = self.sp.queue()
            if not queue['queue']:
                log_output(text_area, "Queue is empty")
                return
                
            log_output(text_area, "\nCurrent Queue:")
            for i, track in enumerate(queue['queue'][:5], 1):  # Show first 5 tracks
                artists = ", ".join([artist['name'] for artist in track['artists']])
                log_output(text_area, f"{i}. {track['name']} - {artists}")
        except Exception as e:
            log_output(text_area, f"Error viewing queue: {e}")

    def add_to_queue(self, query, text_area):
        """Add a track to the queue"""
        try:
            # Search for the track
            results = self.sp.search(q=query, limit=1, type='track')
            if not results['tracks']['items']:
                log_output(text_area, f"No results found for '{query}'")
                return
                
            track = results['tracks']['items'][0]
            self.sp.add_to_queue(uri=track['uri'])
            artists = ", ".join([artist['name'] for artist in track['artists']])
            log_output(text_area, f"Added to queue: {track['name']} - {artists}")
        except Exception as e:
            log_output(text_area, f"Error adding to queue: {e}")

    def get_detailed_track_info(self, text_area):
        """Get detailed information about current track"""
        try:
            current = self.sp.current_playback()
            if not current or not current['item']:
                log_output(text_area, "No track currently playing")
                return
    
            track = current['item']
            features = self.sp.audio_features(track['id'])[0]
            
            # Format duration
            duration_ms = track['duration_ms']
            duration = f"{duration_ms // 60000}:{(duration_ms % 60000) // 1000:02d}"
            
            # Get track popularity
            popularity = track['popularity']
            
            info = f"""
Detailed Track Information:
--------------------------
Title: {track['name']}
Artist(s): {', '.join(artist['name'] for artist in track['artists'])}
Album: {track['album']['name']}
Release Date: {track['album']['release_date']}
Duration: {duration}
Popularity: {popularity}/100

Audio Features:
--------------
Key: {features['key']}
Tempo: {int(features['tempo'])} BPM
Danceability: {int(features['danceability'] * 100)}%
Energy: {int(features['energy'] * 100)}%
Acousticness: {int(features['acousticness'] * 100)}%
Instrumentalness: {int(features['instrumentalness'] * 100)}%
Valence (Positivity): {int(features['valence'] * 100)}%

Currently {'Playing' if current['is_playing'] else 'Paused'}
Progress: {current['progress_ms'] // 1000}s / {duration}
"""
            log_output(text_area, info)
        except Exception as e:
            log_output(text_area, f"Error getting track info: {e}")

def handle_spotify(arguments, _, text_area, __, self):
    """Handle Spotify commands"""
    if not hasattr(handle_spotify, 'controller'):
        handle_spotify.controller = SpotifyController()
    
    if not handle_spotify.controller.is_connected:
        log_output(text_area, "Error: Spotify controller not properly initialized")
        return
    
    if not arguments:
        log_output(text_area, """
Spotify Commands:
----------------
spotify play <song name> - Search and play a song
spotify pause - Pause/resume playback
spotify next - Play next track
spotify prev - Play previous track
spotify shuffle - Toggle shuffle mode
spotify status - Show current track info
spotify volume <0-100> - Set volume
spotify playlists - List your playlists
spotify playlist play <name> - Play a specific playlist
spotify playlist create <name> - Create a new playlist
spotify recommend - Get song recommendations
spotify queue - View current queue
spotify queue add <song name> - Add song to queue
spotify info - Get detailed track information
""")
        return
        
    command = arguments[0].lower()
    
    # New volume command
    if command == "volume" and len(arguments) > 1:
        handle_spotify.controller.set_volume(arguments[1], text_area)
    
    # Playlist commands
    elif command == "playlists":
        handle_spotify.controller.list_playlists(text_area)
    elif command == "playlist":
        if len(arguments) < 3:
            log_output(text_area, "Usage: spotify playlist [play|create] <name>")
            return
        if arguments[1] == "play":
            handle_spotify.controller.play_playlist(" ".join(arguments[2:]), text_area)
        elif arguments[1]== "add":
            handle_spotify.controller.add_current_playing_to_playlist(" ".join(arguments[2:]), text_area)
            
        elif arguments[1] == "create":
            handle_spotify.controller.create_playlist(" ".join(arguments[2:]), text_area)
    
    # Recommendation command
    elif command == "recommend":
        handle_spotify.controller.get_recommendations(text_area)
    
    # Queue commands
    elif command == "queue":
        if len(arguments) > 1 and arguments[1] == "add":
            handle_spotify.controller.add_to_queue(" ".join(arguments[2:]), text_area)
        else:
            handle_spotify.controller.view_queue(text_area)
    
    # Detailed info command
    elif command == "info":
        handle_spotify.controller.get_detailed_track_info(text_area)
    
    # Basic playback commands
    elif command == "play":
        if len(arguments) > 1:
            # Search and play a specific song
            query = " ".join(arguments[1:])
            handle_spotify.controller.search_and_play(query, text_area)
        else:
            # Resume playback of current track
            handle_spotify.controller.play_pause(text_area)
    
    elif command == "pause":
        handle_spotify.controller.play_pause(text_area)
    
    elif command == "next":
        handle_spotify.controller.next_track(text_area)
    
    elif command == "prev":
        handle_spotify.controller.previous_track(text_area)
    
    elif command == "shuffle":
        handle_spotify.controller.toggle_shuffle(text_area)
    
    elif command == "status":
        handle_spotify.controller.get_current_track(text_area)
    
    else:
        log_output(text_area, f"Unknown Spotify command: {command}")
        log_output(text_area, "Type 'spotify' without arguments to see available commands")




