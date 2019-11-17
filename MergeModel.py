#This script merges the two inp files containing the part
#definitions of blade and vein part into a single model.
#Then it sets up all the necessary task of model building
#such as material definition, constrains etc.

from sys import path
from abaqus import *
import utiinternal
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
import pickle
import math
import os
import mesh
import part
import assembly
import material
import section
import interaction
import regionToolset
executeOnCaeStartup()
#: Executing "onCaeStartup()" in the site directory ...

#Copy the input files.

path="Z:/Documents/Dropbox/MSME/thesis/abaqus_temp/"
inpFile1 = path+'blade.inp'
inpFile2 = path+'vein_mesh.inp'
model="Leaf"
fname=path+'Leaf.cae'

def get_nodes(part_name):
    
    p = mdb.models[model].parts[part_name]
    k=len(p.nodes)
    node=[]
    for i in range (0,k):
        node.append(p.nodes[i].coordinates)

    return node


def get_elements(part_name):
    
    p = mdb.models[model].parts[part_name]
    k=len(p.elements)
    element=[]
    for i in range (0,k):
        element.append(p.elements[i].connectivity)
    
    return element

def distance_p2p(loc1,loc2):
    
    return math.sqrt((loc1[0]-loc2[0])**2+(loc1[1]-loc2[1])**2+(loc1[2]-loc2[2])**2)


Mdb()
mdb.ModelFromInputFile(name='Blade', inputFileName=inpFile1)
mdb.ModelFromInputFile(name='Vein', inputFileName=inpFile2)
mdb.Model(name='Leaf')
mdb.models['Leaf'].Part('Vein', mdb.models['Vein'].parts['VEIN'])
mdb.models['Leaf'].Part('Blade', mdb.models['Blade'].parts['BLADE_ALONE'])
del mdb.models['Blade']
del mdb.models['Vein']
del mdb.models['Model-1']

#Material 
print "Defining materials"
mdb.models['Leaf'].Material(name='Material-1')
mdb.models['Leaf'].materials['Material-1'].Density(table=((0.5e-9, ), ))
mdb.models['Leaf'].materials['Material-1'].Elastic(table=((100, 0.3), ))

mdb.models['Leaf'].Material(name='Material-2')
mdb.models['Leaf'].materials['Material-2'].Density(table=((0.5e-9, ), ))
mdb.models['Leaf'].materials['Material-2'].Elastic(table=((5000, 0.3), ))

#Section
print "Defining sections"
mdb.models['Leaf'].HomogeneousShellSection(name='Section-1', \
    preIntegrate=OFF, material='Material-1', thicknessType=UNIFORM, \
    thickness=1, thicknessField='', idealization=NO_IDEALIZATION, \
    poissonDefinition=DEFAULT, thicknessModulus=None, temperature=GRADIENT, \
    useDensity=OFF, integrationRule=SIMPSON, numIntPts=5)

mdb.models['Leaf'].CircularProfile(name='Profile-1', r=2)

mdb.models['Leaf'].BeamSection(name='Section-2', profile='Profile-1', \
    integration=DURING_ANALYSIS, poissonRatio=0.0, material='Material-2', \
    temperatureVar=LINEAR)


#assigning section
print "Assigning sections"
p = mdb.models['Leaf'].parts['Blade']
f = p.faces
region = regionToolset.Region(faces=f)
p.SectionAssignment(region=region, sectionName='Section-1', offset=0.0, \
    offsetType=MIDDLE_SURFACE, offsetField='')

p = mdb.models['Leaf'].parts['Vein']
e = p.edges
region = regionToolset.Region(edges=e)
p.SectionAssignment(region=region, sectionName='Section-2', offset=0.0, \
    offsetType=MIDDLE_SURFACE, offsetField='')


nodes=pickle.load(open( path+"node_data", "rb" ))   
vein_structures=pickle.load(open( path+"point_list", "rb" ))  
elements=pickle.load(open( path+"element_data", "rb" ))

node_list=[]
for vein_structure in vein_structures:
    t=[]
    for node in vein_structure:
        t.append(nodes.index(node))
    node_list.append(t)

pickle.dump(node_list,open( path+"node_list", "wb" ))

#finds breached elements
print "Finding breached elements"

breach_elem=[]
for i in range(0,len(node_list)):
    temp1=node_list[i]
    for j in range(0,len(temp1)-1):
        for k in range(0,len(elements)):
            temp2=list(elements[k])
            if len(temp2)==4:
                if ((temp1[j])in temp2 and (temp1[j+1]) in temp2):
                    a=temp2.index(temp1[j])
                    b=temp2.index(temp1[j+1])   
                    if math.fabs(b-a)==2:
                        t=[k,a]
                        breach_elem.append(t)
                                     
pickle.dump(breach_elem,open( path+"breach_elem", "wb" )) 

#gets node and element info of part vein
nodes=get_nodes('Vein')
elements=get_elements('Vein')
pickle.dump(nodes,open( path+"node_data_2", "wb" ))  
pickle.dump(elements,open( path+"element_data_2", "wb" ))
#sets constrains
print "Setting constrains"
points=pickle.load(open(path+"point_list","rb"))
#nodes1=pickle.load(open(path+"node_data","rb"))
nodes1=get_nodes('Blade')
print nodes1

nodes2=get_nodes('Vein')
print nodes2
#nodes2=pickle.load(open(path+"node_data_2","rb"))
p = mdb.models[model].parts['Blade']
mdb.models[model].rootAssembly.Instance(name='Blade-1', part=p, dependent=ON)
p = mdb.models[model].parts['Vein']
mdb.models[model].rootAssembly.Instance(name='Vein-1', part=p, dependent=ON)
a = mdb.models[model].rootAssembly
p1=a.instances['Blade-1']
p2=a.instances['Vein-1']

check=[]
k=0
l=0

for i in range (0,len(points)):
    for j in range (0,len(points[i])):
        if points[i][j] in check :
            pass
        else:
            check.append(points[i][j])
            #k1=nodes1.index(points[i][j])
            d=[]
            for m in range(0,len(nodes1)):
                t=distance_p2p(points[i][j],nodes1[m])
                d.append(t)
                
            k1=d.index(min(d))
            
            d=[]
            for m in range(0,len(nodes2)):
                t=distance_p2p(points[i][j],nodes2[m])
                d.append(t)
                
            k2=d.index(min(d))
            if (k1<len(nodes1)):
                n1=p1.nodes[k1:k1+1]
            else:
                n1=p1.nodes[-1]
                
            if (k2<len(nodes2)):
                n2=p2.nodes[k2:k2+1]
            else:
                n2=p2.nodes[-1]

            a.Set(nodes=n1,name='Set-'+str(k+1))
            a.Set(nodes=n2,name='Set-'+str(k+2))
            mdb.models[model].Tie(name='Con-'+str(l+1),master=a.sets['Set-'+str(k+2)],slave=a.sets['Set-'+str(k+1)],adjust=OFF)
            k=k+2
            l=l+1
mdb.saveAs(pathName=fname)
mdb.close() 
