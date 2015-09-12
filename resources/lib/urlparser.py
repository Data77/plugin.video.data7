import mrknow_urlparser

class urlparser:
  def __init__(self):
    self.up = mrknow_urlparser.mrknow_urlparser()

  def getVideoLink(self, url,referer=''):
    return self.up.getVideoLink(url, referer);