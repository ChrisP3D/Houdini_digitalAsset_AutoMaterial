import os    

node = hou.pwd()

geo = node.geometry()

#the separator symbol inside of the filename
separator = node.parm('separator').evalAsString()

currentContext = node.parent()

upperContext = currentContext.parent()

children = currentContext.children()

#material network in which to add nodes
contextEval = node.parm('material_context').evalAsString()

if hou.node(contextEval) in children:
    parent = hou.node(contextEval)

else:
    newMatNet = currentContext.createNode('matnet')
    newMatPosition = (node.position().x() +2,node.position().y())
    newMatNet.setPosition(newMatPosition)
    newContext = node.setParms({'material_context': newMatNet.path()})
    
    parent = hou.node(newContext)


#folder in which to load texture files from
parentfolder = node.parm('From_Parent_Folder').evalAsString()

#declair name constants and create other constant nodes
rsTextureNode = "redshift::TextureSampler"
rsMaterialNode = "redshift::Material"

connectTo = parent.createNode(rsMaterialNode, "connectTo")
displaceNode = parent.createNode("redshift::Displacement", "RsDisplacement")
bumpNode = parent.createNode("redshift::BumpMap", "RsBumpMap")

mainOutputNode = parent.createNode("redshift_material", "redshift_material_output")

mainOutputNode.setInput(0,connectTo,0)
mainOutputNode.setInput(1,displaceNode,0)
mainOutputNode.setInput(2,bumpNode,0)


diffuseList = ['Diffuse', 'diffuse','abledo']
translucencyList = ['Translucency', 'translucency','TranslucencyColor']
rehRoughList = ['ReflRoughness','Roughness']
opacityList = ['opacity', 'Opacity', 'Transparency']

needToConnect = [diffuseList, translucencyList, rehRoughList,opacityList]


RSinputKey = {'diffuse': 0,
            'translucency': 3,
            'reflectionRoughness': 7,
            'opacity': 50,
            'translucencyWeight': 4}
            

def findAndConnect(checklist,name, inputIndentifier,node):
    for i in checklist:
        i = name
        if i in checklist:
            node.setInput(RSinputKey[inputIndentifier], newNode,0)


#Gather file paths into a list


filepaths = []

for root, dirs, files in os.walk(os.path.abspath(parentfolder)):
    for file in files:
        path = os.path.join(root, file)
        filepaths.append(path)
    
        
#ExtractNames by separator parameter into a list
           
filenames = []

for file in filepaths:
    splitfile = file.split(separator)
    splitfilename = splitfile[-1]
    newname = splitfilename.split(".exr")[0]
    filenames.append(newname)

newNodes = []

for count, file in enumerate(filepaths):
    name = filenames[count]
    setpath = filepaths[count]
    
    newNode = parent.createNode(rsTextureNode, name)
    newNode.name = filenames[count]

    newName = newNode.name
    
    #TODO: find the other textures
    findAndConnect(diffuseList,newName,'diffuse', connectTo)    
    findAndConnect(translucencyList,newName,'translucency', connectTo)
    findAndConnect(opacityList,newName,'opacity',connectTo)
    
    if name == 'TranslucencyWeight':
        connectTo.setInput(4, newNode, 0)
    if name == 'Normal':
        bumpNode.setInput(0, newNode,0)
    if name == 'Displacement':
        displaceNode.setInput(0, newNode,0)  
    if name == 'ReflRoughness':
        connectTo.setInput(7,newNode,0)
        
     # set paths
    newNode.setParms({"tex0": filepaths[count]})
    newNodes.append(newNode)


parent.layoutChildren()

