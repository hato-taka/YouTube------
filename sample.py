from apiclient.discovery import build
import pandas as pd
import json

with open('secret.json') as f:
    secret = json.load(f)

DEVELOPER_KEY = secret['KEY']
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# def youtube_search(options):
# 認証を行っている部分
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                developerKey=DEVELOPER_KEY)

# 関数化する
def video_search(youtube, q='自動化', max_results=50):
    response = youtube.search().list(
        q=q,
        part='id,snippet',
        order='viewCount',
        type='video',
        maxResults=max_results
    ).execute()

    items = response['items']
    items_id = []
    for item in items:
        item_id = {}
        item_id['video_id'] = item['id']['videoId']
        item_id['channel_id'] = item['snippet']['channelId']
        items_id.append(item_id)

    df_video = pd.DataFrame(items_id)
    return df_video

df_video = video_search(youtube)
channel_ids = df_video['channel_id'].unique().tolist()

subscriber_list = youtube.channels().list(
    id=','.join(channel_ids),
    part='statistics',
    fields='items(id, statistics(subscriberCount))'
).execute()

def json_print(data):
    print(json.dumps(data, indent=4, ensure_ascii=False))

subscribers = []
for item in subscriber_list['items']:
    subscriber = {}
    subscriber['channel_id'] = item['id']
    subscriber['subscriber_count'] = int(item['statistics']['subscriberCount'])
    subscribers.append(subscriber)

df_subscribers = pd.DataFrame(subscribers)

df = pd.merge(left=df_video, right=df_subscribers, on='channel_id')

df_extracted = df[df['subscriber_count'] < 5000]

video_ids = df_extracted['video_id'].tolist()
video_list = youtube.videos().list(
    id=','.join(video_ids),
    part='snippet,statistics',
    fields='items(id,snippet(title),statistics(viewCount))'
).execute()

videos_info = []
items = video_list['items']

for item in items:
    video_info = {}
    video_info['video_id'] = item['id']
    video_info['title'] = item['snippet']['title']
    video_info['viewCount'] = item['statistics']['viewCount']
    videos_info.append(video_info)

df_videos_info = pd.DataFrame(videos_info)

results = pd.merge(left=df_extracted, right=df_videos_info, on='video_id')
print(results[:3])

# json_print(videos_info[:5])