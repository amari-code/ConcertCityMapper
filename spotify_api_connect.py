import spotipy
from spotipy.oauth2 import SpotifyOAuth
import secret_id


artist_list = []
last_id = None
SPOTIPY_CLIENT_ID = secret_id.client_id
SPOTIPY_CLIENT_SECRET = secret_id.client_secret
count = 0
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri="http://localhost:7777/callback",
                                               scope="user-follow-read"))


while True:
    results = sp.current_user_followed_artists(limit=50, after=last_id)
    for artist in results['artists']['items']:
        #print(artist['name'])
        artist_list.append(artist['name'])
        last_id = artist['id']
        count += 1
    if results['artists']['next'] == None:
        break


# results = sp.current_user_followed_artists(limit=50, after='7yxi31szvlbwvKq9dYOmFI')
# print(results)

# text = json.dumps(results, sort_keys=True, indent=4)
# print(text)