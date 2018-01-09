#!/usr/bin/python
import random
import numpy
#global all_set
server1_ip = '192.168.140.1'
server2_ip = '192.168.140.2'
server3_ip = '192.168.140.3'
server4_ip = '192.168.140.4'
server5_ip = '192.168.140.5'
server6_ip = '192.168.140.6'
server7_ip = '192.168.140.7'
server8_ip = '192.168.140.8'
struct_of_fault_domains={
  'room1':{
    'carbinet1':{
      'power1_1':[
         server1_ip,
         server2_ip
      ],
      'power1_2':[
         server3_ip,
         server4_ip
      ]
    },
    'carbinet2':{
      'power2_1':[
         server5_ip,
         server6_ip
      ],
      'power2_2':[
         server7_ip,
         server8_ip
      ]
    }
  }
}
'''
获取最高级非平凡故障域数量
如果当前故障域有多个则故障域非平凡，该故障域为最高级非平凡故障域，直接返回该故障域的值。
如果当前故障域只有一个，比如room1，则向下递归，直到找到故障域大于1为止。
'''
def get_domain_num(fault_domains):
    if len(fault_domains) > 1:
        top_domain = fault_domains
        num_of_domain = len(fault_domains)
        return top_domain,num_of_domain
    elif len(fault_domains) == 1:
        return get_domain_num(fault_domains[list(fault_domains)[0]])
'''
整数拆分函数
将一个整数拆分为N个整数，比如5可以拆分为[1,1,1,1,1]/[1,1,1,2]/[1,2,2]/[1,1,3]/[2,3]
'''
def SpliteUnit(lens, step, arr, index, results, seg=3):
    if lens == 0:
        if seg == index:
            all_set.append(arr[:index])
        results.append(arr[:index])
    for i in range(step, lens + 1, 1):
        arr[index] = i
        SpliteUnit(lens - i, i, arr, index + 1, results, seg)
'''
选取方差最小整数拆分方案
如果有5个consul server要分布在3个最高级非平凡故障域上则需要将5这个数字拆成三份，那么可能会有[1,1,3]/[1,2,2]两
种方案，但是为了将故障的重叠率降到最低，则需要部署consulserver分布在尽量分散的故障域上，如此[1,2,2]会优
于[1,1,3]，此时需要利用列表方差值来选取最优方案
'''
def get_best_set(consul_server_num, seg):
    num = consul_server_num
    result = []
    tmp_arr = [0] * num
    global all_set
    all_set = []
    SpliteUnit(num, 1, tmp_arr, 0, result, seg)
    if len(all_set) > 1:
        variance = numpy.var(all_set[0])
        best = all_set[0]
        for i in all_set[1:]:
            if numpy.var(i) < variance:
                variance = numpy.var(i)
                best = i
    else:
        best = all_set[0]
    return best
#获取consulserver部署节点
def get_consul_node(top_domain, domain_num, consul_server_num=2):
    consul_servers = []
    '''
    如果最高级非平凡故障域数量大于consul server数量，则随机选取与consul server数量相等的最高级非平凡故障域。
    向下查找直到找到最终的服务器IP，随机抽取其中一个作为consul server
    '''
    if domain_num >= consul_server_num:
        consul_domains = {}
        cur_domain = {}
        if  isinstance(top_domain, dict):
            for i in random.sample(top_domain, consul_server_num):
                consul_domains[i]=top_domain[i]
            for key in consul_domains.keys():
                cur_domain = consul_domains[key]
                #@print cur_domain
                while isinstance(cur_domain, dict):
                    cur_domain = cur_domain[str(random.sample(cur_domain, 1)[0])]
                consul_server = random.sample(cur_domain, 1)[0]
                #print consul_server
                consul_servers.append(consul_server)
        else:
            consul_servers = random.sample(top_domain, consul_server_num)
        return consul_servers
    '''
    如果最高级非平凡故障域数量小于consul server数量则将consul_server_num进行拆分成与故障域数量相同的数字（调用get_best_set方法获取最优）。
    轮询拆分后的数组，如果下级的故障域数量大于等于上级故障域分配的consul数量则上面的代码会执行并返回consul_server节点，否则继续向下递归。
    '''
    else:
        consul_sets = get_best_set(consul_server_num, domain_num)
        i = 0
        for key in top_domain.keys():
            consul_in_domain = consul_sets[i]
            cur_domain,subdomain_num = get_domain_num(top_domain[key])
            #print cur_domain, subdomain_num, consul_in_domain
            consul_servers.append(get_consul_node(cur_domain, subdomain_num, consul_in_domain))#向下递归
            i = i+1
        return consul_servers
#    else
#def get_server_num():
#    ...
#print random.sample(struct_of_fault_domains['room1'], 1)
consul_server_num = 2
server_num = 51
if server_num > 50:
    consul_server_num = 5
else:
    consul_server_num = 3
top_domain,domain_num = get_domain_num(struct_of_fault_domains)
print get_consul_node(top_domain,domain_num, consul_server_num)
