# i2p主动探测

> readme写的很乱，后续有需要再写

用于进行i2p节点的主动探测，基本思路是用本地的客户端与i2p结点建立TCP连接，然后发一些奇奇怪怪的包，看看该节点的反应是否符合之前对于i2p结点的预期

## 特征汇总

1. 如果上次主动断掉连接的话，下次就直接加黑名单，连不上
2. 如果连接的时间超过10秒，那么对方会主动的断开连接
3. 如果连接一直没有到64bit这个阈值，那么服务端会一直接收，直到超时断开连接
4. 如果数据的前8个字节内容之前发送过，会引发**重放中断**
5. 从64字节~192字节，被中断的概率会呈现线性，即64字节的包被中断概率为0，192字节的包被中断概率为1，128字节的包被中断概率为0.5

除此之外，节点可能因为网络原因直接TCP握手之后RST，这个也是需要考虑的

节点在达到64字节的阈值之后，可能会直接进行PK中断，因为这里PK中断需要用到i2p结点的routerinfo相关的内容，所以无法利用该特征，另该特征会妨碍我们进行探测

## i2p节点库爬虫
大概7分钟~8分钟完成一次爬虫


## 测试用例
### 2023-11-30

1. 连接持续时间测试

   建立连接之后，一直发送1byte的数据，直到连接被对方中断，看这个连接的时间，如果连接的时间在9s到13s之间，那么该测试通过，否则不通过，超过13s主动中断连接

2. 数据包大小测试

   建立连接之后，一直发送32字节的数据，直到连接被对方中断，最后发出去的包数量应在3个到6个之间，如果2个的话，那么就是未知（PK）

3. 重放中断测试

   建立连接之后，还是一直发送32字节的数据，并且数据的前8个字节和测试2中一致，最后发出去的包的数量应该是2个

4. 数据包大小测试

   建立连接之后，先发送63字节的包，然后持续发送129字节的包，最后发出去的包的数量应该是2个

5. 黑名单测试

   建立连接之后，发送1字节的数据，之后主动断开连接，然后再次连接，如果连接之后被立即RST，说明测试通过



### 主动探测
action1：

action2：进行三轮测试，每一轮测试都测两个测试用例(C++, Java)



