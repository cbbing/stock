# coding=utf-8

'''
作者:Jairus Chan
程序:多项式曲线拟合算法
'''
import matplotlib.pyplot as plt
import math
import numpy
import random

#阶数为9阶
order=9

#进行曲线拟合
def getMatA(xa):
    matA=[]
    for i in range(0,order+1):
        matA1=[]
        for j in range(0,order+1):
            tx=0.0
            for k in range(0,len(xa)):
                dx=1.0
                for l in range(0,j+i):
                    dx=dx*xa[k]
                tx+=dx
            matA1.append(tx)
        matA.append(matA1)
        
    matA=numpy.array(matA)    
    return matA

def getMatB(xa,ya):
    matB=[]
    for i in range(0,order+1):
        ty=0.0
        for k in range(0,len(xa)):
            dy=1.0
            for l in range(0,i):
                dy=dy*xa[k]
            ty+=ya[k]*dy
        matB.append(ty)
     
    matB=numpy.array(matB)
    return matB

def getMatAA(xa, ya):
    matAA=numpy.linalg.solve(getMatA(xa),getMatB(xa, ya))
    return matAA

#设置阶数（默认为9
def setOrder(newOrder):
    order = newOrder

#获取拟合后的新序列    
def getFitYValues(xValues, yValues, xNewValues):
    matAA_get = getMatAA(xValues, yValues)
    
    yya=[]
    
    for i in range(0,len(xNewValues)):
        yy=0.0
        for j in range(0,order+1):
            dy=1.0
            for k in range(0,j):
                dy*=xNewValues[i]
            dy*=matAA_get[j]
            yy+=dy
        yya.append(yy)
        
    return yya    
#画出拟合后的曲线
#print(matAA)

if __name__ == "__main__":

    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    #生成曲线上的各个点
    x = numpy.arange(-1,1,0.02)
    y = [((a*a-1)*(a*a-1)*(a*a-1)+0.5)*numpy.sin(a*2) for a in x]
    #ax.plot(x,y,color='r',linestyle='-',marker='')
    #,label="(a*a-1)*(a*a-1)*(a*a-1)+0.5"
    
    #生成的曲线上的各个点偏移一下，并放入到xa,ya中去
    i=0
    xa=[]
    ya=[]
    for xx in x:
        yy=y[i]
        d=float(random.randint(60,140))/100
        #ax.plot([xx*d],[yy*d],color='m',linestyle='',marker='.')
        i+=1
        xa.append(xx*d)
        ya.append(yy*d)
    
    '''for i in range(0,5):
        xx=float(random.randint(-100,100))/100
        yy=float(random.randint(-60,60))/100
        xa.append(xx)
        ya.append(yy)'''
    
    ax.plot(xa,ya,color='m',linestyle='',marker='.')

    matAA_n = getMatAA(xa,ya)
    print len(matAA_n)
    
    xxa= numpy.arange(-1,1.2,0.01)
    yya= getFitYValues(xa, ya, xxa)
  
    ax.plot(xxa,yya,color='g',linestyle='-',marker='')
    
    ax.legend()
    plt.show()