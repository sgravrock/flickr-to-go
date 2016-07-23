class MockRequests:
    def __init__(self, contents=None):
        self.contents = {} if contents is None else contents

    def get(self, url):
        if url not in self.contents:
            raise UnmockedUrlException('Un-mocked URL: ' + url)
        return MockResponse(self.contents[url])

class MockResponse:
    def __init__(self, content):
        self.content = content

class UnmockedUrlException(Exception):
    pass
