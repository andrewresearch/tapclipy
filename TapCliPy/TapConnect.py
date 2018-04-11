from TapCliPy import queries
from urllib import request,response
import json

class Connect:
    def __init__(self,url='http://localhost:9000',endpoint='/graphql'):
        self.fullurl = url+endpoint

    def url(self):
        return self.fullurl

    def analyseText(self, query, text):
        variables = {'input': text}
        escapedQuery = query.replace("\n", "\\n")  # query.encode('utf8').decode('unicode_escape')
        fullQuery = json.dumps({'query': escapedQuery, 'variables': variables})
        jsonHeader = {'Content-Type': 'application/json'}
        tapReq = request.Request(self.fullurl, data=fullQuery.encode('utf8'), headers=jsonHeader)
        tapResponse = ""
        try:
            tapResponse = request.urlopen(tapReq)
            body = tapResponse.read().decode('utf8')
            return json.loads(body)
        except Exception as e:
            print(e)
            return json.dumps({})

    def query(self,name):
        return queries.query[name]
