import sys,os
import re

class Valid():

	def __init__(self):

		self.patternC = r'(\~|\`|\!|\@|\#|\$|\%|\^|\&|\*|\+|\=|\\|\?|\<|\>|\{|\}|\[|\]|:|,)+'
		self.patternD = r'(\~|\`|\!|\@|\#|\$|\%|\^|\&|\*|\-|\+|\=|\\|\/|\?|\<|\>|\{|\}|\[|\]|:|;|\(|\))+|(\,' \
						r')+|([a-zA-Z]|[а-яА-Я])+'

	def validString(self, text):

		res = re.search(self.patternC, text)
		if res != None:
			return False
		else:
			return True

	def validDigit(self, digit):

		res = re.search(self.patternD, digit)
		if res != None:
			return False
		else:
			return True

	def escape(self, text):

		res0 = re.sub(r'"', u'\\"', text)
		res = re.sub(r'\s', u'\ ', res0)

		return res

	def validSString(self, *args, **kwargs):

		for i in args:
			res = re.search(self.patternC, i)
			if res != None:
				return False

		return True
