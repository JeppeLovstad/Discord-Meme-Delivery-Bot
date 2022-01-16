import requests
from requests.auth import HTTPBasicAuth
from random import choice
from utils.iniparser import getConfigAsDict

class RedditScrape:
    def __init__(self, sub_reddit = "python", load_amount = 100,post_type = 'all'):
        self.sub_reddit = sub_reddit
        self.load_amount = load_amount
        self.post_dictionary = {}
        self.post_type = post_type
        if not self.setup_reddit_API_config():
            raise Exception("Reddit Scrape missing config")
            
    def setup_reddit_API_config(self):
        config = getConfigAsDict("REDDITSCRAPE")
        if len(config) != 4:
            return False
            
        # note that CLIENT_ID refers to 'personal use script' and SECRET_TOKEN to 'token'
        self.auth = HTTPBasicAuth(config["client_id"], config["secret_token"])
        # here we pass our login method (password), username, and password
        self.data = {'grant_type': 'password',
                'username': config["username"],
                'password': config["password"]}
        
        # setup our header info, which gives reddit a brief description of our app
        self.headers = {'User-Agent': 'MemeBot/0.0.1'}
        
        return True


    def get_reddit_api_token_header(self):
        # send our request for an OAuth token
        res = requests.post('https://www.reddit.com/api/v1/access_token',
                            auth=self.auth, data=self.data, headers=self.headers)
        
        # convert response to JSON and pull access_token value
        TOKEN = res.json()['access_token']

        # add authorization to our headers dictionary
        return {**self.headers, **{'Authorization': f"bearer {TOKEN}"}}

    def get_random_post(self):
        if(len(self.post_dictionary) < 5):# and len(self.post_dictionary > 0)):
            self.populate_list()
            
        if not self.post_dictionary:
            return {"title":"Link dictionary is empty :(", "url":"" }
         
        key = choice(list(self.post_dictionary))
        post = self.post_dictionary[key]
        self.post_dictionary.pop(key)
        return post

    def populate_list(self):
        request_header_with_token = self.get_reddit_api_token_header()
        # while the token is valid (~2 hours) we just add headers=headers to our requests
        res = requests.get("https://oauth.reddit.com/r/"+self.sub_reddit+"/hot",
                   headers=request_header_with_token, params = {'limit': str(self.load_amount)})

        #print(res.json())
        for idx, post in enumerate(res.json()['data']['children']):
                
            title = post['data']['title']
            url = post['data']['url']
                
            if (self.post_type == 'img' and url[-4:] in ('.jpg','.png','.gif','webm')):
                post_info = {'title' :title,'url' : url}
                self.post_dictionary[idx] = post_info
                continue
            
            if (self.post_type == 'all'):
                post_info = {'title' : title,'url' : url}
                self.post_dictionary[idx] = post_info
                continue
            
           
        
