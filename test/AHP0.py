   
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False #用来正常显示负号
#%% 相关性检验
index=pd.read_excel('index.xlsx', index_col = u'省份')



def test(data):   
    plt.subplots(figsize=(16, 16)) # 设置画面大小
    sns.heatmap(data, annot=True, vmax=1, square=True, cmap="Blues")
    plt.savefig('./BluesStateRelation.png')
    plt.show()
    
    
test(index.corr())


#%% 权重确定
matrix=pd.read_excel('matrix0.xlsx')
matrix=matrix.fillna(0).astype(float)

for i in range(len(matrix)):
    for j in range(len(matrix)):
        if matrix.iloc[i,j]!=0:
            continue
        else:
            matrix.iloc[i,j]=1/matrix.iloc[j,i]

def weightVector(matrix,method='root'):        
    if method=='root':
        weight0=matrix.cumprod(axis=1).iloc[:,-1]**(1/(len(matrix)))
        weight1=weight0/weight0.sum()
    elif method=='sum':       
        matrix0=matrix/matrix.cumsum(axis=0).iloc[-1,:]
        weight0=matrix0.cumsum(axis=1).iloc[:,-1]
        weight1=weight0/weight0.sum()
    else:
        print('method should take argument root or sum')
    return(weight1)

def matrixWeightAndConsistencyCheck(matrix,method='root',accuracy=4):
    RI=[0, 0, 0.58, 0.9, 1.12, 1.24, 1.32, 1.41, 1.45, 1.49, 1.51]   
    WI=weightVector(matrix,method=method)
    n=len(WI)
    if n>11:
        print('Index supposed to be less than 12')
    if n>2:
        judgeW=matrix.dot(WI)
        la_max =(judgeW/WI).sum()/n
        CI = (la_max - n)/(n - 1)
        CR = CI/RI[n]
        print('CI=%s,CR=%s'%(CI,CR))
        if CR <= 0.1:
            print(" 通过一致性检验 ")
#            print(" WI: %s"%list(WI))
        else:
            print(" 请调整判断矩阵,使CR<0.1 \n")
            WI = np.nan   
    elif n <= 2:
        WI=WI
    return(round(WI,accuracy))
    
    
weight=matrixWeightAndConsistencyCheck(matrix,method='root')

#%% 数据标准化
def autoDynamicRatingLevelAndIndex(data_series,type='quantile',k=4,index=False):
    if type=='distance':
        w=k 
        c=(data_series.max()-data_series.min())/k
        w=list(range(k+1)*c) 
    elif type=='quantile':
        w = [1.0*i/k for i in range(k+1)]
        w = list(data_series.quantile(w))#describe(percentiles = w)[4:4+k+1] #使用describe函数自动计算分位数
    elif type=='kmean':
        kmodel = KMeans(n_clusters = k, n_jobs = 1) #建立模型，n_jobs是并行数，一般等于CPU数较好
        kmodel.fit(data_series.round(2).values.reshape((len(data_series), 1))) #训练模型
        c = pd.DataFrame(kmodel.cluster_centers_).sort_values(0) #输出聚类中心，并且排序（默认是随机序的）
        w = c.rolling(2).mean().dropna()#相邻两项求中点，作为边界点
        w = [data_series.min()] + list(w[0]) + [data_series.max()] 
    else:
        raise Exception('Invalid types') 
    wb=w.copy()
    wb[0]=wb[0]-abs(wb[1])
    wb[-1]=wb[-1]+abs(wb[-2])
    d = pd.cut(data_series, wb, labels = range(k)).astype(str).astype(int)
#    d.name=rename+'风险评级'
    d_out=d.copy()
    if index==True:
        d_index=d.copy()
        for k in list(set(d)):           
            d_index[d==k]=(data_series[d==k]-w[k])/(w[k+1]-w[k])+k 
 #       d_index.name=rename+'风险指数'
        d_out=d_index
    return(d_out)




index=pd.read_excel('index.xlsx', index_col = u'省份')
index_index=index.copy()

for i in list(index.columns):    
    index_index[i]=autoDynamicRatingLevelAndIndex(index[i],type='quantile',k=10,index=True)

negativeindex=['政府性债务余额','债务率(显性)', '负债率(显性)']
#postiveindex=list(set(list(index.columns)).difference(set(negativeindex)))    
WI=[0.1]*8+[0.2]
WI_col=pd.concat([pd.Series(index.columns),pd.Series(WI)],axis=1)
WI_col.columns=['指标名称','权重']

for j in negativeindex:
    WI_col.loc[WI_col.指标名称==j,'权重']=-WI_col.loc[WI_col.指标名称==j,'权重']

mappingsocres=-WI_col[WI_col.权重<0].权重.sum()*10

index_index_standard=index_index.copy()
for m,n in zip(list(WI_col.权重),list(WI_col.指标名称)):
    index_index_standard[n]=index_index[n]*m
    
name='地方政府债务风险指数'
index_index_standard[name]=index_index_standard.T.sum()+mappingsocres








