# -*- coding: utf-8 -*-
# @Time    : 2018/9/6 下午2:13
# @Author  : shijie luan
# @Email   : lsjfy0411@163.com
# @File    : demo_protocol.py
# @Software: PyCharm

'''
本模块主要是为了和10个协议的仿真接轨，可以复用数据库模块、server模块、分类模块

鉴于FANUC蜜罐已经实现了各模块，所以此模块改动前可参照上述提到的几个模块

基本思路：
    1.筛选10个协议：需要 请求（最好是nmap脚本的，没有也可以标明功能）—— 应答对
    2.数据库存储：id-请求-应答-协议-功能，复用connect_database.py(用来连接数据库)、
                具体数据库的填充用人工还是自动化填充，看心情，如果自动化的就可以复用docker_mysql.py
    3.分类：复用classify.py，目前只做10个协议单一类的，所以在模版一侧添加的数据只需要一个协议一个dict即可
    4.切换：启动时，每个协议对应server端的一个socket，绑定一个端口，若存在多个协议对应一个端口，则复用该端口


注意：只有协议和端口都稳合才可以回复响应的回复
'''

import binascii
import socket
import threading
import time
import sys
import logging
import mylog

data = [
#fox
{'request_data':'056405c900000000364c',
'response_data':'0564058b01006400a097',
'function':'get_fox_info', 'id': 1},
{'request_data':'056408c40200030036ace0c1181490',
'response_data':'05640a44030002005382d5c1810000f82f',
'function':'get_fox_info', 'id': 2},
{'request_data':'',
'response_data':'05640bc40100640044eac4c7013c010683f4',
'function':'get_fox_info', 'id': 3}
]

log = mylog.myLog()
#056405c900000000364c056405c901000000de8e056405c9020000009f84056405c9030000007746056405c9040000001d90056405c905000000f552056405c906000000b458056405c9070000005c9a056405c90800000019b9056405c909000000f17b056405c90a000000b071056405c90b00000058b3056405c90c0000003265056405c90d000000daa7056405c90e0000009bad056405c90f000000736f056405c91000000011eb056405c911000000f929056405c912000000b823056405c91300000050e1056405c9140000003a37056405c915000000d2f5056405c91600000093ff056405c9170000007b3d056405c9180000003e1e056405c919000000d6dc056405c91a00000097d6056405c91b0000007f14056405c91c00000015c2056405c91d000000fd00056405c91e000000bc0a056405c91f00000054c8056405c920000000014f056405c921000000e98d056405c922000000a887056405c9230000004045056405c9240000002a93056405c925000000c251056405c926000000835b056405c9270000006b99056405c9280000002eba056405c929000000c678056405c92a0000008772056405c92b0000006fb0056405c92c0000000566056405c92d000000eda4056405c92e000000acae056405c92f000000446c056405c93000000026e8056405c931000000ce2a056405c9320000008f20056405c93300000067e2056405c9340000000d34056405c935000000e5f6056405c936000000a4fc056405c9370000004c3e056405c938000000091d056405c939000000e1df056405c93a000000a0d5056405c93b0000004817056405c93c00000022c105605c93d000000ca03056405c93e0000008b09056405c93f00000063cb056405c940000000584a056405c941000000b088056405c942000000f182056405c9430000001940056405c9440000007396056405c9450000009b54056405c946000000da5e056405c947000000329c056405c94800000077bf056405c9490000009f7d056405c94a000000de77056405c94b00000036b5056405c94c0000005c63056405c94d000000b4a1056405c94e000000f5ab056405c94f0000001d69056405c9500000007fed056405c951000000972f056405c952000000d625056405c9530000003ee7056405c9540000005431056405c955000000bcf3056405c956000000fdf9056405c957000000153b056405c9580000005018056405c959000000b8da056405c95a000000f9d0056405c95b0000001112056405c95c0000007bc4056405c95d0000009306056405c95e000000d20c056405c95f0000003ace056405c9600000006f49056405c961000000878b056405c962000000c681056405c9630000002e43056405c96400000044905
#666f7820612031202d3120666f782068656c6c6f0a7b0a666f782e76657273696f6e3d733a312e300a69643d693a310a686f73744e616d653d733a7870766d2d306f6d64633031786d790a686f7374416464726573733d733a3139322e3136382e312e3132350a6170702e6e616d653d733a576f726b62656e63680a6170702e76657273696f6e3d733a332e372e34340a766d2e6e616d653d733a4a61766120486f7453706f7428544d292053657276657220564d0a766d2e76657273696f6e3d733a32302e342d6230320a6f732e6e616d653d733a57696e646f77732058500a6f732e76657273696f6e3d733a352e310a6c616e673d733a656e0a74696d655a6f6e653d733a416d65726963612f4c6f735f416e67656c65733b2d32383830303030303b333630303030303b30323a30303a30302e3030302c77616c6c2c6d617263682c382c6f6e206f722061667465722c73756e6461792c756e646566696e65643b30323a30303a30302e3030302c77616c6c2c6e6f76656d6265722c312c6f6e206f722061667465722c73756e6461792c756e646566696e65640a686f737449643d733a57696e2d393943422d443439442d353434322d303742420a766d557569643d733a38623533306263382d373663352d343133392d613265612d3066616264333934643330350a6272616e6449643d733a76796b6f6e0a7d3b3b0a
#63000000000000000000000000000000c1debed100000000
#63000000000000000000000000000000c1debed100000000
#70001c0001002a00000000000000000000000000000000000000000001000200a1000400224095ffb1000800e7000602208e2401
# 0300007d02f080320700000000000c0060000112081284010100000000ff09005c00110001001c0003000136455337203231352d31414734302d3058423020000000012020000636455337203231352d31414734302d3058423020000000012020000736455337203231352d31414734302d3058423020000056040000
# data = {id:1,
#  'request_data':'',
# 'response_data':'',
# 'protocol':'S7',
# 'functions':'get_info'}
def processRecv(strRecv):
    all = strRecv.split('05640')
    # print(all)

    for i in all:
        if i == '':
            all.remove(i)
    # if all[0] == '' and all[-1]:
    #     all.remove('')
    if all != []:
        for i in range(len(all)):
            all[i] = '05640' + all[i]
            # print(all[i])
    else:
        # 此处设置警报信息
        # 造成这种情况的包一般是'a0a0a0a0'或''
        pass
    # print(all)
    return all

def b2a_str(data_temp):
    # 将网络字节流转为ascii码
    data_recv = binascii.b2a_hex(data_temp)
    data_recv = data_recv.decode('utf-8')
    # print(type(str(data)))
    # 将字节流转为list
    request_list = processRecv(data_recv)

    return request_list

def processRequest(request):
    return 0

def findresponse(request,search):
    #此处的request为ascii码格式
    for i in data:
        if i[search] == request:
            return binascii.a2b_hex(i['response_data'])

def dnp3link(sock,addr):

    # time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    # print(type(addr))
    # print("{0} Accept new connection from {1}:{2}".format(time_now, addr[0], addr[1]))
    log.info("{0} Accept new connection from {1}:{2}".format(" ", addr[0], addr[1]))
    count = 0
    # id = 1
    while True:
        if count <= 100:
            try:
                data_temp = sock.recv(1024)
                if data_temp != b'':
                    # print(data_temp)
                    # print(count)
                    # time.sleep(0.1)
                    data_recv = b2a_str(data_temp)

                    while data_recv:
                        i = data_recv[0]
                        # time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                        log.info("%s request:%s" % (" ", i))
                        # print("%s request:%s" % (time_now, i))
                        # if request_list[0]['function'] == 'cotp' and request_list[0]['id'] < 1:
                        #     id += 1
                        # else:
                        try:

                            response_data = findresponse(i,'request_data')
                            sock.send(response_data)
                            # time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                            # print("%s response:%s" % (time_now, binascii.b2a_hex(response_data)))
                            log.info("%s response:%s" % (" ", binascii.b2a_hex(response_data)))
                            # print("response:%s\r\n"%(binascii.b2a_hex(response_data)))
                            # id = 2
                            data_recv.remove(i)
                            count = 0

                        except:
                            count = 0
                            # time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                            # print('%s response cannot find!' % time_now)
                            log.warning('%s response cannot find!' % "WoW!")
                            # print('response cannot find!%s'%i)
                            #没有时，随便发
                            sock.send(binascii.a2b_hex('0564058b01006400a097'))
                            # print("%s response:%s" % (time_now, '0564058b01006400a097'))
                            log.warning("%s response:%s" % ("Lucky!", '0564058b01006400a097'))
                            # print("response:%s\r\n"%("0564058b01006400a097"))
                            data_recv.remove(i)


                    # elif id == 2:
                    #     response_data = findresponse(id, 'id')
                    #     sock.send(response_data)
                    #     print("response:%s\r\n"%(binascii.b2a_hex(response_data)))
                    #     id += 1
                    #     count = 0
                    # else:
                        count += 1

            except:
                count += 1
                # print('no request!')
                # sock.send(binascii.a2b_hex('0300001611d00005001000c0010ac1020100c2020200'))

        else:
            # time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            # print("%s connection from %s:%s has been broken!" % (time_now, addr[0], addr[1]))
            log.warning("%s connection from %s:%s has been broken!" % (" ", addr[0], addr[1]))
            break
        time.sleep(0.2)
    sock.close()


def opendnp3(ip,port=20000):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # s1.bind(('127.0.0.1', 102))
    # s.bind(('192.168.127.94', 1911))
    s.bind((ip, 20000))
    # 设置最大连接数
    s.listen(100)
    # s.setblocking(0)
    # s.setblocking(0)
    # print('Waiting for connecting...')
    log.info('Waiting for connecting...')

    '''
    建立连接的server
    '''

    while True:
        sock, addr = s.accept()
        # 设置为非阻塞式
        # sock.setblocking(False)
        t = threading.Thread(target=dnp3link, args=(sock, addr))
        t.start()
    #
        print("ok")

# 可以封装成函数，方便 Python 的程序调用
def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip

if __name__ == "__main__":
    # request = binascii.a2b_hex("0300001611e00000000500c1020100c2020200c0010a")
    # indata = b2a_str(request)
    # for i in indata:
    #     response = findresponse(i)
    #     print(response)
    # opens7()
    ip_addr = get_host_ip()
    if ip_addr == '':
        # ip_port = sys.argv[1]
        # else:
        try:
            ip_addr = sys.argv[1]
            # ip_port = sys.argv[2]
        except:
            # print("error, You have to input your ip address")
            log.error("ip configuration error!!!")
    opendnp3(ip_addr)
# print(find(data))




