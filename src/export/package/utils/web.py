import urllib.request

from bs4 import BeautifulSoup

def getHtml(url):
  request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
  response = urllib.request.urlopen(request)
  return response.read()


def getHtmlParser(markup):
	return BeautifulSoup(markup, "html.parser")