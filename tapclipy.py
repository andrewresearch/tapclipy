
class PyTap:
    def __init__(self,url='http://localhost:9000/graphql'):
        self.url = url

    def currentUrl(self):
        return self.url
