#!/usr/bin/env python
# coding: utf-8

# In[85]:


def read_text(select,attribute=0): #function for reading scraped data
    from bs4 import BeautifulSoup
    text=[]
    
    for tag in select:
        if attribute==0:
            text.append(tag.get_text())
        else:
            text.append(tag[attribute])
            
    return text


# In[86]:


def create_hot100_df(): #Function to get the latest update of the top100 hot billboard list
    import pandas as pd
    import requests
    from bs4 import BeautifulSoup

    url = "https://www.billboard.com/charts/hot-100"
    response = requests.get(url)
    
    hot100= BeautifulSoup (response.content,"html.parser")
    
    title=read_text(hot100.select("span.chart-element__information__song.text--truncate.color--primary"))
    artists=read_text(hot100.select("span.chart-element__information__artist.text--truncate.color--secondary"))
    last_week=read_text(hot100.select("span.chart-element__meta.text--center.color--secondary.text--last"))
    peak_rank=read_text(hot100.select("span.chart-element__information__delta__text.text--peak"))
    weeks_on=read_text(hot100.select("span.chart-element__information__delta__text.text--week"))
    
    billboard_df=pd.DataFrame({"Song title":title,
                               "Artists involved":artists,
                               "Rank Last Week":last_week,
                               "Peak Rank": peak_rank,
                               "Weeks on": weeks_on 
                              })
    
    return billboard_df


# In[87]:


def input_song(df): #Function to read user's input
    import pandas as pd
    
    song=""   
    song=(input("Write down one of your favourite songs : "))
    ret_song=[]
        
    if song.lower() in df.str.lower().values : 
        
        ret_song.append(True)
        
    else:
        
        ret_song.append(False)
    
    ret_song.append(song)
        
    return ret_song


# In[88]:


def random_song(df): #Function to return a random song from the top100 hot songs
    import pandas as pd
    
    new_song=df["Song title"].sample()
    song_artist=df["Artists involved"][df["Song title"]==list(new_song)[0]]
           
    return new_song , song_artist


# In[89]:


def get_playlist_tracks(username,playlist_id): #Function to read a whole playlist from Spotify
    import spotipy 
    from spotipy.oauth2 import SpotifyClientCredentials
    
    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
        client_id='82c7549d6f7e4453871ce606e4752b70',
        client_secret='785b5199900e4ea9a1fa042790cd2ae4'
        ))
    
    results = spotify.user_playlist_tracks(username,playlist_id)
    tracks = results['items']
    
    while results['next']:
        results = spotify.next(results)
        tracks.extend(results['items'])
        
    return tracks


# In[90]:


def get_details_tracks(result): #Functions to get the song names, artists and audio features from a Spotify dictionary
    import spotipy 
    from spotipy.oauth2 import SpotifyClientCredentials
    
    song_names=[]
    song_uri=[]
    artist_names=[]
    artist_uri=[]
    features=[]
    flat_features=[]
    song_details=[]
    i=0
    
    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
        client_id='82c7549d6f7e4453871ce606e4752b70',
        client_secret='785b5199900e4ea9a1fa042790cd2ae4'
        ))
    
    for item in result:
        
        if item["is_local"] == False:
            
            i+=1
            song_names.append(item["track"]["name"])
            artist_names.append(item["track"]["artists"][0]["name"])
            artist_uri.append(item["track"]["artists"][0]["uri"])
            song_uri.append(item["track"]["uri"])
            
            if i==100:
                
                i=0
                features.append(spotify.audio_features(song_uri))
                song_uri=[]
    
    features.append(spotify.audio_features(song_uri)) 
    
    flat_features = [f for subfeatures in features for f in subfeatures]
    
    song_details.append(song_names)
    song_details.append(artist_names)
    song_details.append(flat_features)
        
    
    return song_details , artist_uri


# In[91]:


def clean_features(featureslist):
    
    danceability=[]    
    energy=[]
    loudness=[]
    speechiness=[]
    acousticness=[]
    instrumentalness=[]
    liveness=[]
    valence=[]
    tempo=[]
    duration_ms=[]
    all_features=dict()
    
    for feature in featureslist:
               
        danceability.append(feature["danceability"])
        energy.append(feature["energy"])
        loudness.append(feature["loudness"]) 
        speechiness.append(feature["speechiness"]) 
        acousticness.append(feature["acousticness"])         
        instrumentalness.append(feature["instrumentalness"]) 
        liveness.append(feature["liveness"]) 
        valence.append(feature["valence"])
        tempo.append(feature["tempo"]) 
        duration_ms.append(feature["duration_ms"])
            
        all_features={"danceability" : danceability,
                  "energy" : energy,
                  "loudness" : loudness,
                  "speechiness" : speechiness,
                  "acousticness" : acousticness,
                  "instrumentalness" : instrumentalness,
                  "liveness" : liveness,
                  "valence" : valence,
                  "tempo" : tempo,
                  "duration_ms" : duration_ms                  
                 }
        
    return all_features
    


# In[92]:


def run(original_df_top,original_df_spotify):
    
    from bs4 import BeautifulSoup
    import pandas as pd
    import numpy as np
    import pickle
    from sklearn.preprocessing import StandardScaler
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
    
    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
        client_id='82c7549d6f7e4453871ce606e4752b70',
        client_secret='785b5199900e4ea9a1fa042790cd2ae4'
        ))
    
    df=original_df_top.copy()
    df_spotify=original_df_spotify.copy()
    ask_another=""
    user_input = input_song(df["Song title"])
    chosen_song = user_input[1]
    x=0 
    
    #removing  user input song from dataframe so it doesn't come back as recommendation
    df.drop(df[df['Song title'].str.lower()==chosen_song.lower()].index,inplace=True)
    
    while user_input[0]==True and x==0:
        
        new_song , new_artist = random_song(df) 
             
        print("\n\nHere's our recommendation based in your previous choice :\n\nSong title : '"+
              list(new_song)[0]+"'\nInterpreted by : '"+list(new_artist)[0]+"'\n")
        
        while True:
            
            ask_another=(input("\nDo you want another recommendation based on your choice? y/n : "))
            
            if ask_another.lower()=="n":
                
                print("\nThanks for using our services!")
                x=1
                break
                
            elif ask_another.lower()=="y":
                
                #Droping actual recommendation so it doesn't repeat for the next one
                df.drop(df[df['Song title']==list(new_song)[0]].index,inplace=True)
                break
                
            else:
                
                print("\nThat's neither 'y' or 'n', try again: do you want another recommendation? y/n : ")
            
                
    if user_input[0]==False:
        
        kmeans = pickle.load(open("kmeans", "rb"))
        scaler = pickle.load(open("scaler", "rb"))
        
        artist=(input("Write down the name of the artist interpeting your previous song choice : "))
        
        while True:
            try:

                results = spotify.search(q="track:"+chosen_song+" artist:"+artist,limit=10)
                print("\nYour song choice was '"+(results["tracks"]["items"][0]["name"])+"' interpreted by '"+str(results["tracks"]["items"][0]["artists"][0]["name"])+"'")
                audio_features_df=pd.DataFrame(spotify.audio_features(results["tracks"]["items"][0]["uri"]))
                break
    
            except IndexError: #Adding except in case the input song is not found in the spotify database

                print("\n\nSORRY! , we didn't find that song in the spotify database, try again with another song please...\n\n")
                chosen_song=(input("\nWrite down one of your favourite songs : "))
                artist=(input("\nWrite down the name of the artist interpeting your previous song choice : "))

        
        #Picking the same features i used in my clustering: 
        audio_features=audio_features_df[["danceability","energy","loudness","speechiness","acousticness","instrumentalness","liveness","valence","tempo"]]
        chosen_song_cluster=kmeans.predict(scaler.transform(audio_features))
        
        while True:
            
            recommended_song=df_spotify[["Title","Artists"]][df_spotify["Cluster"] == chosen_song_cluster[0]].sample()
            
            s_name = list(recommended_song["Title"])
            s_artist = list(recommended_song["Artists"])
            
            print("\nHere goes our recommendation song based in your previous choice :\n\n\n'"+str(s_name[0])+
                  "' interpreted by '"+str(s_artist[0])+"'")
        
            ask_another=(input("\n\n\nDo you want another recommendation based on your choice? y/n : "))
            
            if ask_another.lower()=="n":
                
                print("\nThanks for using our services!")
                break
                
            elif ask_another.lower()=="y":
                
                #Droping actual recommendation so it doesn't repeat for the next one
                df_spotify.drop(df_spotify[df_spotify['Title']==str(s_name[0])].index,inplace=True)
                
            else:
                
                print("\nThat's neither 'y' or 'n', try again: do you want another recommendation? y/n : ")
        

