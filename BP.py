# coding=utf-8
# Back-Propagation Neural Networks
# http://blog.csdn.net/akunainiannian/article/details/40073903

import math
import random
import string

random.seed(0)

# calculate a random number where:  a <= rand < b
def rand(a, b):
    return (b-a)*random.random() + a

# Make a matrix (we could use NumPy to speed this up)
def makeMatrix(I, J, fill=0.0):
    m = []
    for i in range(I):
        m.append([fill]*J)
    return m

# our sigmoid function, tanh is a little nicer than the standard 1/(1+e^-x)
#使用双正切函数代替logistic函数
def sigmoid(x):
    return math.tanh(x)

# derivative of our sigmoid function, in terms of the output (i.e. y)
# 双正切函数的导数，在求取输出层和隐藏侧的误差项的时候会用到
def dsigmoid(y):
    return 1.0 - y**2

class NN:
    def __init__(self, ni, nh, no):
        # number of input, hidden, and output nodes
        # 输入层，隐藏层，输出层的数量，三层网络
        self.ni = ni + 1 # +1 for bias node
        self.nh = nh
        self.no = no

        # activations for nodes
        self.ai = [1.0]*self.ni
        self.ah = [1.0]*self.nh
        self.ao = [1.0]*self.no
        
        # create weights
        #生成权重矩阵，每一个输入层节点和隐藏层节点都连接
        #每一个隐藏层节点和输出层节点链接
        #大小：self.ni*self.nh
        self.wi = makeMatrix(self.ni, self.nh)
        #大小：self.ni*self.nh
        self.wo = makeMatrix(self.nh, self.no)
        # set them to random vaules
        #生成权重，在-0.2-0.2之间
        for i in range(self.ni):
            for j in range(self.nh):
                self.wi[i][j] = rand(-0.2, 0.2)
        for j in range(self.nh):
            for k in range(self.no):
                self.wo[j][k] = rand(-2.0, 2.0)

        # last change in weights for momentum 
        #?
        self.ci = makeMatrix(self.ni, self.nh)
        self.co = makeMatrix(self.nh, self.no)

    def update(self, inputs):
        if len(inputs) != self.ni-1:
            raise ValueError('wrong number of inputs')

        # input activations
        # 输入的激活函数，就是y=x;
        for i in range(self.ni-1):
            #self.ai[i] = sigmoid(inputs[i])
            self.ai[i] = inputs[i]

        # hidden activations
        #隐藏层的激活函数,求和然后使用压缩函数
        for j in range(self.nh):
            sum = 0.0
            for i in range(self.ni):
                #sum就是《ml》书中的net
                sum = sum + self.ai[i] * self.wi[i][j]
            self.ah[j] = sigmoid(sum)

        # output activations
        #输出的激活函数
        for k in range(self.no):
            sum = 0.0
            for j in range(self.nh):
                sum = sum + self.ah[j] * self.wo[j][k]
            self.ao[k] = sigmoid(sum)

        return self.ao[:]

    #反向传播算法 targets是样本的正确的输出
    def backPropagate(self, targets, N, M):
        if len(targets) != self.no:
            raise ValueError('wrong number of target values')

        # calculate error terms for output
        #计算输出层的误差项 
        output_deltas = [0.0] * self.no
        for k in range(self.no):
            #计算k-o
            error = targets[k]-self.ao[k]
            #计算书中公式4.14
            output_deltas[k] = dsigmoid(self.ao[k]) * error

        # calculate error terms for hidden
        #计算隐藏层的误差项，使用《ml》书中的公式4.15
        hidden_deltas = [0.0] * self.nh
        for j in range(self.nh):
            error = 0.0
            for k in range(self.no):
                error = error + output_deltas[k]*self.wo[j][k]
            hidden_deltas[j] = dsigmoid(self.ah[j]) * error

        # update output weights
        # 更新输出层的权重参数
        # 这里可以看出，本例使用的是带有“增加冲量项”的BPANN
        # 其中，N为学习速率 M为充量项的参数 self.co为冲量项
        # N: learning rate
        # M: momentum factor
        for j in range(self.nh):
            for k in range(self.no):
                change = output_deltas[k]*self.ah[j]
                self.wo[j][k] = self.wo[j][k] + N*change + M*self.co[j][k]
                self.co[j][k] = change
                #print N*change, M*self.co[j][k]

        # update input weights
        #更新输入项的权重参数
        for i in range(self.ni):
            for j in range(self.nh):
                change = hidden_deltas[j]*self.ai[i]
                self.wi[i][j] = self.wi[i][j] + N*change + M*self.ci[i][j]
                self.ci[i][j] = change

        # calculate error
        #计算E(w)
        error = 0.0
        for k in range(len(targets)):
            error = error + 0.5*(targets[k]-self.ao[k])**2
        return error

    #测试函数，用于测试训练效果
    def test(self, patterns):
        for p in patterns:
            print(p[0], '->', self.update(p[0]))

    def weights(self):
        print('Input weights:')
        for i in range(self.ni):
            print(self.wi[i])
        print()
        print('Output weights:')
        for j in range(self.nh):
            print(self.wo[j])

    def train(self, patterns, iterations=1000, N=0.5, M=0.1):
        # N: learning rate
        # M: momentum factor
        for i in range(iterations):
            error = 0.0
            for p in patterns:
                inputs = p[0]
                targets = p[1]
                self.update(inputs)
                error = error + self.backPropagate(targets, N, M)
            if i % 100 == 0:
                print('error %-.5f' % error)


def demo():
    # Teach network XOR function
    pat = [
        [[0], [0]],
        [[2], [1]],
        [[3], [1]],
        [[4], [5]]
    ]

    # create a network with two input, two hidden, and one output nodes
    n = NN(1, 2, 1)
    # train it with some patterns
    n.train(pat)
    # test it
    n.test(pat)



if __name__ == '__main__':
    demo()
