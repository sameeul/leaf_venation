#This script uses the meshed blade part from Abaqus and predefined
#approximate venation structure to create a detailed venation 
#structure using algorithm 1


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
import regionToolset

path="Z:/Documents/Dropbox/MSME/thesis/abaqus_temp/"
fname=path+'model1.cae'
model='Model-1'

point_on_wire=[]
meshsize=2.65    
searcr_radius=meshsize*1.8


def get_nodes(part_name):
    
    p = mdb.models[model].parts[part_name]
    k=len(p.nodes)
    nodes=[]
    for i in range (0,k):
        nodes.append(p.nodes[i].coordinates)

    return nodes


def get_elements(part_name):
    
    p = mdb.models[model].parts[part_name]
    k=len(p.elements)
    elements=[]
    for i in range (0,k):
        elements.append(p.elements[i].connectivity)
    
    return elements


def distance_p2p(loc1,loc2):
    
    return math.sqrt((loc1[0]-loc2[0])**2+(loc1[1]-loc2[1])**2+(loc1[2]-loc2[2])**2)


def get_neighbour_nodes(node):

    loc_n1=[None]*3
    loc_n2=[None]*3

    loc_n1[0]=nodes[(node-1)][0]
    loc_n1[1]=nodes[(node-1)][1]
    loc_n1[2]=nodes[(node-1)][2]
    neighbour_nodes=[]
    k=len(nodes)
    for i in range(0,k):
        if (i!=node-1):
            loc_n2[0]=nodes[i][0]
            loc_n2[1]=nodes[i][1]
            loc_n2[2]=nodes[i][2]
            d=distance_p2p(loc_n1,loc_n2)
            if (d<=search_radius):
                neighbour_nodes.append(i+1)
    
    return neighbour_nodes



def get_points(n1,n2):
#n1= starting node
#n2= end node
    neighbour_nodes=get_neighbour_nodes(n1)

    if n2 in neighbour_nodes:
        return point_on_wire
    else:
        distance=[]
        k=len(neighbour_nodes)
        x1_loc=[None]*3
        x2_loc=[None]*3
        x0_loc=[None]*3

        for i in range (0,k):
            x1_loc[0]=nodes[n1-1][0]
            x1_loc[1]=nodes[n1-1][1]
            x1_loc[2]=nodes[n1-1][2]
            x2_loc[0]=nodes[n2-1][0]
            x2_loc[1]=nodes[n2-1][1]
            x2_loc[2]=nodes[n2-1][2]
            x0_loc[0]=nodes[neighbour_nodes[i]-1][0]
            x0_loc[1]=nodes[neighbour_nodes[i]-1][1]
            x0_loc[2]=nodes[neighbour_nodes[i]-1][2]
            t=distance_p2p(x1_loc,x0_loc)+distance_p2p(x2_loc,x0_loc)
            distance.append(t)

        node=distance.index(min(distance))
# sanity check - discard if already part of vein or equals to n1
        if neighbour_nodes[node] in point_on_wire or neighbour_nodes[node]==n1:
            k=neighbour_nodes[node]
            neighbour_nodes.remove(k)
        
        node=distance.index(min(distance))
        point_on_wire.append(neighbour_nodes[node])
        n1=neighbour_nodes[node]
        return get_points(n1,n2)
            

def draw_line(n1,n2):
        points_on_line=get_points(n1,n2) 
        k=len(t)

        point_list=[None]*(k+2)
        point_list[0]=nodes[n1-1]
        point_list[k+1]=nodes[n2-1]
        for i in range(0,k):
            point_list[i+1]=nodes[points_on_line[i]-1]
        
        point_tuple=tuple(point_list)
        return point_tuple

###
# wrapper section
###
openMdb(path+"model1.cae")

#Reading node and element information from part Blade                
nodes=get_nodes('Blade')
elements=get_elements('Blade')

pickle.dump(nodes,open( path+"node_data", "wb" ))  
pickle.dump(elements,open( path+"element_data", "wb" ))  

# input vein data
vein=[]

while(True):
    a=input("First node: " )
    if (a<1):
        break
    else:
        b=input("Second node: ")
        vein.append((a,b))

pickle.dump(vein,open( path+"vein_data", "wb" ))

#gather nodes on blade to create venation structure
print "Calculating venation structure"

l=len(vein)
point_list=[]

for i in range(0,l):
    point_list.append(draw_line(vein[i][0],vein[i][1]))
    point_on_wire=[] # make it empty for next round

pickle.dump(point_list,open( path+"point_list", "wb" ))    


#creates a part vein
points=pickle.load(open(path+"point_list","rb"))

p = mdb.models[model].Part(name='Vein',dimensionality=THREE_D, type=DEFORMABLE_BODY)
l=len(points)
for i in range(0,l):
    p.WirePolyLine(points=points[i],mergeWire=OFF,meshable=ON)


#mesh vein part
p = mdb.models['Model-1'].parts['Vein']
p.seedPart(size=2.5*meshsize, deviationFactor=0.1)
elemType1 = mesh.ElemType(elemCode='B33', elemLibrary='STANDARD')
e = p.edges
pickedRegions =(e, )
p.setElementType(regions=pickedRegions, elemTypes=(elemType1, ))
p.generateMesh()

p = mdb.models[model].parts['Blade']
mdb.models[model].rootAssembly.Instance(name='Blade-1', part=p, dependent=ON)
p = mdb.models[model].parts['Vein']
mdb.models[model].rootAssembly.Instance(name='Vein-1', part=p, dependent=ON)

mdb.saveAs(pathName=fname)
mdb.close()          
