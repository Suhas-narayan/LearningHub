
from googleapiclient.discovery import build
from textblob import TextBlob 
from IPython.display import HTML

Api_key = 'AIzaSyDfhjdkO7Ez2dn6Yc_wGvgz213rH2rTCj0'

def score_comments(comments):
    comments_text = ' '.join(comments)
    sentiment_score = TextBlob(comments_text).sentiment.polarity

    keywords = ['keyword1', 'keyword2', 'keyword3']  # Update with your keywords
    keyword_score = sum(1 for keyword in keywords if keyword in comments_text.lower())
    comments_score = (0.6 * sentiment_score) + (0.4 * keyword_score)
    return comments_score
    
def score_video(video_info, suggested_video_links, min_views, max_views):
    max_score = float('-inf')
    best_video_info = None
    best_link = None

    for i, link in enumerate(suggested_video_links):
        views = int(video_info[i]['views']) if video_info[i]['views'] != 'N/A' else 0
        n_views = (views - min_views) / (max_views - min_views) if max_views != min_views else 0

        comments_score = score_comments(video_info[i]['comments_list'])
        final_score = (0.3 * n_views) + (0.2 * (int(video_info[i]['likes']) / views if views != 0 else 0)) + (0.1 * (int(video_info[i]['comments']) / views if views != 0 else 0)) + (0.4 * comments_score)
        
        if final_score > max_score:
            max_score = final_score
            best_video_info = video_info[i]
            best_link = link

    return best_video_info, max_score, best_link

try:
    youtube = build('youtube', 'v3', developerKey=Api_key)

    search_query = input('Enter search query: ')
    search_request = youtube.search().list(
        q=search_query,
        part='snippet',
        type='video',
        maxResults=10
    )
    search_response = search_request.execute()

    video_ids = [item['id']['videoId'] for item in search_response['items']]
    videos_info = []
    for video_id in video_ids:
        video_request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_id
        )
        video_response = video_request.execute()
        video_info = video_response['items'][0]

        video_title = video_info['snippet']['title']
        video_duration = video_info['contentDetails']['duration']
        video_likes = video_info['statistics'].get('likeCount', 'N/A')
        video_comments = video_info['statistics'].get('commentCount', 'N/A')
        video_views = video_info['statistics'].get('viewCount', 'N/A')
        comments_request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            pageToken=None
        )
        comments_response = comments_request.execute()
        video_comments_list = [comment['snippet']['topLevelComment']['snippet']['textDisplay'] for comment in comments_response['items']]

        videos_info.append({'id': video_id, 'title': video_title, 'duration': video_duration, 'likes': video_likes, 'comments': video_comments, 'comments_list': video_comments_list, 'views': video_views})

    min_views = min(int(video_info['views']) for video_info in videos_info if video_info['views'] != 'N/A')
    max_views = max(int(video_info['views']) for video_info in videos_info if video_info['views'] != 'N/A')

    suggested_video_links = ['https://www.youtube.com/watch?v=' + video_id for video_id in video_ids]

    best_video_info, max_score, best_link = score_video(videos_info, suggested_video_links, min_views, max_views)


    print("Best Video:")
    print("Title:", best_video_info['title'])
    print("Duration:", best_video_info['duration'])
    print("Likes:", best_video_info['likes'])
    print("Comments:", best_video_info['comments'])
    print("Views:", best_video_info['views'])
    print("Link:", best_link)
    print("Score:", max_score)


    best_video_id = best_video_info['id']
    display(HTML(f"""<iframe width="560" height="315" src="https://www.youtube.com/embed/{best_video_id}" frameborder="0" allowfullscreen></iframe>"""))

except Exception as e:
    print('An error occurred:', str(e))
