import requests
from requests.auth import HTTPBasicAuth
from random import choice

class RedditScrape:

    post_dictionary = dict()
    def __init__(self, sub_reddit = "python", load_amount = 25):
        self.sub_reddit = sub_reddit
        self.load_amount = load_amount
    
    #MemeBotButItsTrash
    #JeppeChrisLasse123
    def get_random_post(self):
        if(len(self.post_dictionary) < 5):# and len(self.post_dictionary > 0)):
            self.populate_list()
      #  if(len(self.post_dictionary) == 0):
       #    await self.populate_list()
        post = choice(list(self.post_dictionary))
        self.post_dictionary.pop(post)
        print(len(self.post_dictionary))
        return post

    def populate_list(self):

        # note that CLIENT_ID refers to 'personal use script' and SECRET_TOKEN to 'token'
        auth = HTTPBasicAuth('n_gaqCyYChHH3k1i6Ea2Tw', 'qh4_ESsCaGLSwYlK_n-omSjuiat9iw')

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

        res = requests.get("https://oauth.reddit.com/r/"+self.sub_reddit+"/hot",
                   headers=headers, params = {'limit': str(self.load_amount)})

        #print(res.json())
        for post in res.json()['data']['children']:
            url = post['data']['url']
            self.post_dictionary[url] = url
        