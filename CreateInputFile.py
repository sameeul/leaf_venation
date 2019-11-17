#This file takes the inp file generated by MergeModel.py
#and take cares of the splitting of breached elements.
#Finally it creates the inp file used for analysis


import pickle
import os

f=open('C:/Temp/Job-1.inp', 'rt')
g=open('C:/Temp/combined_model.inp', 'wt')
PATH="Z:/Documents/Dropbox/MSME/thesis/abaqus_temp/"

breach_elem=pickle.load(open( PATH+"breach_elem", "rb" ))
elements=pickle.load(open( PATH+"element_data", "rb" ))

b_elem=[]
for i in range(0,len(breach_elem)):
    b_elem.append(breach_elem[i][0])
    

for line in f:
    #print line
    g.write(line)
    if 'Element, type=S4' in line:
        break
for line in f:
    #assuming there will be atleast on S3 element
    if 'Element, type=S3' in line or "Nset" in line or "End" in line:
#        #print line
        g.write(line)
        for i in range(0,len(breach_elem)):
            temp2=elements[breach_elem[i][0]]
            a=breach_elem[i][1]
            if a==0:
                new_line= str(breach_elem[i][0]+1)+", "+str(temp2[a]+1)+", "+str(temp2[a+1]+1)+", "+str(temp2[a+2]+1)
                g.write(new_line+'\n')
                g.write(os.linesep)
                new_line=str(i+len(elements)+1)+", "+str(temp2[a+2]+1)+", "+str(temp2[a+3]+1)+", "+str(temp2[a]+1)
                g.write(new_line+'\n')
                g.write(os.linesep)
            elif a==1:
                print breach_elem[i][0]+1,",",temp2[a]+1,",",temp2[a+1]+1,",",temp2[a+2]+1
                new_line= str(breach_elem[i][0]+1)+", "+str(temp2[a]+1)+", "+str(temp2[a+1]+1)+", "+str(temp2[a+2]+1)
                g.write(new_line+'\n')
                g.write(os.linesep)
                print i+len(elements)+1,",",temp2[a+2]+1,",",temp2[a-1]+1,",",temp2[a]+1
                new_line=str(i+len(elements)+1)+", "+str(temp2[a+2]+1)+", "+str(temp2[a-1]+1)+", "+str(temp2[a]+1)
                g.write(new_line+'\n')
                g.write(os.linesep)
            elif a==2:
                print breach_elem[i][0]+1,",",temp2[a]+1,",",temp2[a+1]+1,",",temp2[a-2]+1
                new_line= str(breach_elem[i][0]+1)+", "+str(temp2[a]+1)+", "+str(temp2[a+1]+1)+", "+str(temp2[a-2]+1)
                g.write(new_line+'\n')
                g.write(os.linesep)
                print i+len(elements)+1,",",temp2[a-2]+1,",",temp2[a-1]+1,",",temp2[a]+1
                new_line=str(i+len(elements)+1)+", "+str(temp2[a-2]+1)+", "+str(temp2[a-1]+1)+", "+str(temp2[a]+1)
                g.write(new_line+'\n')
                g.write(os.linesep)
            else:
                print breach_elem[i][0]+1,",",temp2[a]+1,",",temp2[a-3]+1,",",temp2[a-2]+1
                new_line= str(breach_elem[i][0]+1)+", "+str(temp2[a]+1)+", "+str(temp2[a-3]+1)+", "+str(temp2[a-2]+1)
                g.write(new_line+'\n')
                g.write(os.linesep)
                print i+len(elements)+1,",",temp2[a-2]+1,",",temp2[a-1]+1,",",temp2[a]+1
                new_line=str(i+len(elements)+1)+", "+str(temp2[a-2]+1)+", "+str(temp2[a-1]+1)+", "+str(temp2[a]+1)
                g.write(new_line+'\n')
                g.write(os.linesep)
        break
    else:
        elem=line.split(",")[0]
    #print elem
        if (int(elem)-1 in b_elem):
            pass
        else:
        #print line
            g.write(line) 

    #print elem
for line in f:
    g.write(line)
    #print line    
f.close()
g.close()