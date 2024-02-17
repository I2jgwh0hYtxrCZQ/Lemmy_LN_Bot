import pandas
from pythorhead import Lemmy
import requests
import json
import datetime
from dateutil import parser


# The URL of the Light Novel data to download
Url_LightNovels_Json = "https://lnrelease.github.io/data.json"


# Lemmy Details
Lemmy_Instance = r"""https://ani.social"""
Lemmy_User = r"""USERNAME"""
Lemmy_Password = r"""PASSWORD"""

Lemmy_Community = r"lightnovels@ani.social"


# Downloading the Light Novel Details
session = requests.Session()
response = session.get(Url_LightNovels_Json)

if response.status_code != 200:
    print( "Failed - Light Novel Data not downloaded" )
    exit

Json_LightNovels = json.loads(response.content)



# Setting the dates for filterig the data
Time_Now = datetime.datetime.now()

Date_Start_Raw = Time_Now
Date_End_Raw = Time_Now + datetime.timedelta(days=6)

Date_Start = Date_Start_Raw.strftime("%Y-%m-%d")
Date_End = Date_End_Raw.strftime("%Y-%m-%d")

Date_Start_Title = Date_Start_Raw.strftime("%B %d")
Date_End_Title = Date_End_Raw.strftime("%B %d")




# Adding the Headers for the Data
df = pandas.DataFrame( Json_LightNovels["data"] , columns=[ 'Series', 'Link' , 'Publisher', 'Name', 'Volumne', 'Type' , 'Isbn' , 'Release Date' ])



# Correcting the Series, Publisher and Type
for i, row in df.iterrows():

    Index_Series = df.at[i,'Series']
    Index_Publisher = df.at[i,'Publisher']
    Index_Type = df.at[i,'Type']

    df.at[i,'Series'] = Json_LightNovels["series"][Index_Series][1]
    df.at[i,'Publisher'] = Json_LightNovels["publishers"][Index_Publisher]

    if Index_Type == 1:
        df.at[i,'Type'] = '📖'
    elif Index_Type == 2:
        df.at[i,'Type'] = '🖥️'
    elif Index_Type == 3:
        df.at[i,'Type'] = '🖥️📖'
    elif Index_Type == 4:
        df.at[i,'Type'] ='🎧'



# Filtering the data the the required Dates
filtered_df = df.loc[ (df['Release Date'] >= Date_Start) & (df['Release Date'] < Date_End)]
filtered_df = filtered_df.sort_values( by=['Release Date'] )



# Setting up the post Title
Post_Title = "Lightnovels releasing this week: (" + Date_Start_Title + " - " + Date_End_Title + ")"



# Creating the post body / table
Post_Body = """
| Date       | Title                                                              | Volume | Publisher            | Format      |
|------------|--------------------------------------------------------------------|--------|----------------------|-------------|"""

for i, row in filtered_df.iterrows():

    This_ReleaseDate = filtered_df.at[i,'Release Date']
    This_Title = filtered_df.at[i,'Name']
    This_Volume = filtered_df.at[i,'Volumne']
    This_Publisher = filtered_df.at[i,'Publisher']
    This_Format = filtered_df.at[i,'Type']
    
    Post_Body = Post_Body + '\n' + "| " + str(This_ReleaseDate) + " | " + str(This_Title) + " | " + str(This_Volume) + " | " + str(This_Publisher) + " | " + str(This_Format) + " |"




# Logging into Lemmy and submitting the post
lemmy = Lemmy(Lemmy_Instance,request_timeout=2)
lemmy.log_in( Lemmy_User , Lemmy_Password )
community_id = lemmy.discover_community(Lemmy_Community)

lemmy.post.create( community_id , name=Post_Title , body=Post_Body )



# Posting the weekly read post
Date_Start_Raw_WeeklyRead = Time_Now + datetime.timedelta(days=-7)
Date_End_Raw_WeeklyRead = Time_Now + datetime.timedelta(days=-1)

Date_Start_Title_WeeklyRead = Date_Start_Raw.strftime("%B %d")
Date_End_Title_WeeklyRead = Date_End_Raw.strftime("%B %d")

Post_Title_WeeklyRead = 'What light novel(s) have you read this week, and what do you think about it? [' + str(Date_Start_Title_WeeklyRead) + ' - ' + str(Date_End_Title_WeeklyRead) + ']'
Post_Body_WeeklyRead = ''

lemmy.post.create( community_id , name=Post_Title_WeeklyRead , body=Post_Body_WeeklyRead )
