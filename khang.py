import re
import json
import requests

class Users:
    URI_BASE = 'https://www.tiktok.com/'

    def __init__(self):
        self.object = {}
        self.user = ''
        self.statusCode = ''

    def details(self, user):
        if not user:
            raise ValueError('Missing required argument: "user"')

        self.user = self.prepare(user)
        request = self.request()
        response = self.extract(
            r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"([^>]+)>([^<]+)<\/script>',
            request
        )

        validateProps = response['__DEFAULT_SCOPE__']['webapp.user-detail']

        if 'userInfo' not in validateProps:
            self.statusCode = 404

        if self.statusCode:
            return self.template(
                validateProps,
                'userInfo',
                self.object,
                self.statusCode,
                {
                    'user': {
                        'id': 'id',
                        'username': 'nickname',
                        'profileName': 'uniqueId',
                        'avatar': 'avatarMedium',
                        'description': 'signature',
                        'region': 'region',
                        'verified': 'verified',
                    },
                    'stats': {
                        'following': 'followingCount',
                        'follower': 'followerCount',
                        'video': 'videoCount',
                        'like': 'heartCount',
                    },
                }
            )

    def request(self, method='GET', getParams={}):
        headers = {
            'user-agent': 'Mozilla/5.0 (compatible; Google-Apps-Script)'
        }

        response = requests.get(
            self.URI_BASE + '@' + self.user + '/?lang=ru',
            headers=headers
        )

        self.statusCode = response.status_code

        return response.text

    def prepare(self, user):
        if user:
            return user.lower().replace('@', '', 1)

    def extract(self, pattern, text):
        matches = re.findall(pattern, text)
        return json.loads(matches[0][1]) if matches else {}

    def template(self, request_, requestModule, object_, statusCode_, template_={}):
        object_['code'] = statusCode_

        if statusCode_ == 200:
            for userInfoKey, value in template_.items():
                if requestModule in request_ and userInfoKey in request_[requestModule]:
                    for key, values in value.items():
                        if values in request_[requestModule][userInfoKey]:
                            object_.setdefault(userInfoKey, {})[key] = request_[requestModule][userInfoKey][values]
                        else:
                            object_.setdefault(userInfoKey, {})[key] = None
                else:
                    object_.setdefault(userInfoKey, {})

        elif statusCode_ == 404:
            object_['error'] = 'This account cannot be found.'
        else:
            object_['error'] = 'The page cannot load.'

        return json.dumps(object_)
