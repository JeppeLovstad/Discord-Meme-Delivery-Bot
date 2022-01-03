import requests

class RedditScrape:

    def __init__(self, sub_reddit, load_amount, refresh_time_in_hours):
        self.sub_reddit = sub_reddit
        self.load_amount = load_amount
        self.refresh_time_in_hours = refresh_time_in_hours
       
    #MemeBotButItsTrash
    #JeppeChrisLasse123
    def get_reddit():

        # note that CLIENT_ID refers to 'personal use script' and SECRET_TOKEN to 'token'
        auth = requests.auth.HTTPBasicAuth('n_gaqCyYChHH3k1i6Ea2Tw', 'qh4_ESsCaGLSwYlK_n-omSjuiat9iw')

        # here we pass our login method (password), username, and password
        data = {'grant_type': 'password',
                'username': 'MemeBotButItsTrash',
                'password': 'JeppeChrisLasse123'}

        # setup our header info, which gives reddit a brief description of our app
        headers = {'User-Agent': 'MemeBot/0.0.1'}

        # send our request for an OAuth token
        res = requests.post('https://www.reddit.com/api/v1/access_token',
                            auth=auth, data=data, headers=headers)
        
        # convert response to JSON and pull access_token value
        TOKEN = res.json()['access_token']

        # add authorization to our headers dictionary
        headers = {**headers, **{'Authorization': f"bearer {TOKEN}"}}

        # while the token is valid (~2 hours) we just add headers=headers to our requests
        requests.get('https://oauth.reddit.com/api/v1/me', headers=headers)

        res = requests.get("https://oauth.reddit.com/r/python/hot",
                   headers=headers)

        for post in res.json()['data']['children']:
            print(post['data']['title'])
        
r = RedditScrape
r.get_reddit()