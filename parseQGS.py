from qgis.core import *
from qgis.gui import *
from PyQt5.QtCore import QFileInfo
import json
import unicodedata
import sys

project = 'ctbb'
project_path = '/home/gerald/Documents/PSIG/ctbb/parse/'
#project_file = 'poum.qgs'
#project_file = 'guia'
#project_file = 'ortofotos_historial'
#project_file = 'activitats'

prj_file = sys.argv[1]
project_file = prj_file.replace('.qgs', '')

# create a reference to the QgsApplication, setting the
# second argument to False disables the GUI
qgs = QgsApplication([], False)

# supply path to qgis install location
qgs.setPrefixPath("/usr", True)

# load providers
qgs.initQgis()

# Get the project instance
project = QgsProject.instance()
gui = QgsGui.instance()

# Load qgis project
if not project.read(project_path+prj_file):
    print('Something went wrong with the project file!')

print("Project file:", project.fileName())
print("Project title: ", project.title())

def replaceSpecialChar(text):
    chars = "!\"#$%&'()*+,./:;<=>?@[\\]^`{|}~"
    for c in chars:
        text = text.replace(c, "")
    return text

def stripAccents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

def layertree(node):
	#print(node.dump())
	#print(node.name(), type(node))
	obj = {}

	if isinstance(node, QgsLayerTreeLayer):
		obj['name'] = node.name()
		obj['mapproxy'] = project+"_"+project_file+"_layer_"+replaceSpecialChar(stripAccents(obj['name'].lower().replace(' ', '_')))
		obj['type'] = "layer"
		obj['indentifiable'] = node.layerId() not in nonidentify
		obj['visible'] = node.isVisible()
		obj['hidden'] = node.name().startswith("@")
		if obj['hidden']:
			obj['visible'] = True 	# hidden layers/groups have to be visible by default
		obj['showlegend'] = not node.name().startswith("~")
		obj['fields'] = []
		obj['actions'] = []
		#print("- layer: ", node.name())
		
		layer = project.mapLayer(node.layerId())

		if obj['indentifiable']:
			for index in layer.attributeList():
				if layer.editorWidgetSetup(index).type() != 'Hidden':
					#print(layer.fields()[index].name(), layer.attributeDisplayName(index))

					f = {}
					#f['name'] = layer.fields()[index].name()
					#f['alias'] = layer.attributeDisplayName(index)
					f['name'] = layer.attributeDisplayName(index)
					obj['fields'].append(f)

			for action in gui.mapLayerActionRegistry().mapLayerActions(layer):
				a = {}
				a['name'] = action.name()
				a['action'] = action.action()
				obj['actions'].append(a)
		
		return obj

	elif isinstance(node, QgsLayerTreeGroup):
		obj['name'] = node.name()
		obj['mapproxy'] = project+"_"+project_file+"_group_"+replaceSpecialChar(stripAccents(obj['name'].lower().replace(' ', '_')))
		obj['type'] = "group"
		obj['visible'] = node.isVisible()
		obj['hidden'] = node.name().startswith("@")
		if obj['hidden']:
			obj['visible'] = True 	# hidden layers/groups have to be visible by default
		obj['children'] = []
		#print("- group: ", node.name())
		#print(node.children())

		for child in node.children():
			obj['children'].append(layertree(child))

	return obj

info=[]
# print("Project tree:")
nonidentify = project.nonIdentifiableLayers()
root = project.layerTreeRoot()
for group in root.children():
	obj = layertree(group)
	info.append(obj)

# identifiable <Identify>
#print(project.readEntry("qgis", "Identify"))

# write to json file
f=open(prj_file+'.json', 'w+')
f.write(json.dumps(info))
f.close()
#QgsVectorFileWriter.writeAsVectorFormat(i,dataStore + os.sep + 'exp_' + safeLayerName + '.js', 'utf-8', exp_crs, 'GeoJSON', layerOptions=['COORDINATE_PRECISION=3'])

# When your script is complete, call exitQgis() to remove the
# provider and layer registries from memory
qgs.exitQgis()
