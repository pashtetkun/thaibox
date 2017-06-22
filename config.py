import sys, os
from lxml import etree


class Config:

	def __init__(self):
		self.configfile = ''
		self.config_path = ''
		self.config_file = ''
		self.base_path = []
		self.base_file = ''

	def createConfig(self):

		conf = etree.Element("configure")
		etree.SubElement(conf, "id").text = "configfile"
		etree.SubElement(conf, "filename").text = "config.xml"
		confstr = etree.tostring(conf)
		base = etree.Element("database")
		etree.SubElement(base, "id").text = "base"
		#etree.SubElement(base, "path").text = os.getcwd()
		etree.SubElement(base, "path").text = ''
		etree.SubElement(base, "filename").text = "basedb.db"
		basestr = etree.tostring(base)

		root = etree.Element("application")
		root.append(etree.XML(confstr))
		root.append(etree.XML(basestr))
		handle = etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True)
		xmlfile = open(self.configfile, "w")
		xmlfile.writelines(handle.decode('utf-8'))
		xmlfile.close()

	def readconfig(self):
		pwd = os.getcwd()

		# TODO: проверить путь под win и lin (они различатся)
		self.configfile = os.path.join(pwd, 'config.xml')
		try:
			#platform = sys.platform
			#if platform == 'linux':
			tree = etree.ElementTree(file=self.configfile)
			self.config_file = tree.xpath('/application/configure/filename/text()')
			self.base_path = tree.xpath('/application/database/path/text()')
			self.base_file = tree.xpath('/application/database/filename/text()')
			return tree

		except IOError as e:
			print('\nERROR - can find file: %s\n' % e)
			self.createConfig()
			print('Created ...')
			tree = etree.ElementTree(file=self.configfile)
			return tree

	def updateconfig(self, path):

		tree = self.readconfig()
		node = tree.find('database')
		node_el = node.find('path')
		node_el.text = path
		handle = etree.tostring(tree, pretty_print=True, encoding='utf-8', xml_declaration=True)
		xmlfile = open(self.configfile, "w")
		xmlfile.writelines(handle.decode('utf-8'))
		xmlfile.close()
		#print(path)
		#print(tree)



