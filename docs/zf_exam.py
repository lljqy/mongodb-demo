import secrets
from pprint import pprint
from typing import Optional, List

# 第⼀题（必答）
# 实现⼀个类，⽤来存储⼀个班级的学号。实现以下⽅法：
# ● 添加⼀个学号
# ● 查找⼀个学号是否存在（O1）
# ● 删除⼀个学号
# ● 随机返回⼀个学号
# ● 返回⼀个最⼩的学号（O1）
"""
思路：
  1. 查询单个学号需要使用O(1)时间复杂度，所以用一个hash表保存所有学生学号
  2. 返回最小学号使用O(1)时间复杂度，需要一个小根堆来维护所有的学号，heap[0]就是最小学号
  3. 由于堆中的元素无法及时删除，用一个set来保存删除了的学生学号，当堆顶元素在删除set中时进行惰性删除"""


class Heap:

    def __init__(self) -> None:
        self._heap = list()
        self._heapify()

    @property
    def values(self) -> List[int]:
        return self._heap

    @property
    def top(self) -> int:
        return self.values[0]

    def _modify_up(self, pos: int) -> None:
        end = len(self._heap)
        start = pos
        el = self._heap[pos]
        child = 2 * pos + 1
        while child < end:
            right = child + 1
            if right < end and self._heap[child] >= self._heap[right]:
                child = right
            self._heap[pos] = self._heap[child]
            pos = child
            child = 2 * pos + 1
        self._heap[pos] = el
        self._modify_down(start, pos)

    def _modify_down(self, start: int, pos: int) -> None:
        el = self._heap[pos]
        while pos > start:
            parent_pos = (pos - 1) >> 1
            parent = self._heap[parent_pos]
            if el < parent:
                self._heap[pos] = parent
                pos = parent_pos
                continue
            break
        self._heap[pos] = el

    def _heapify(self) -> None:
        n = len(self._heap)
        for index in reversed(range(n >> 1)):
            self._modify_up(index)

    def push(self, el: int) -> None:
        self._heap.append(el)
        self._modify_down(0, len(self._heap) - 1)

    def pop(self) -> int:
        last_el = self._heap.pop()
        if self._heap:
            return_el = self._heap[0]
            self._heap[0] = last_el
            self._modify_up(0)
            return return_el
        return last_el


class Student:
    FAIL = False
    SUCCESS = True

    def __init__(self) -> None:
        self._student_ids = set()
        self._small_heap = Heap()
        self._deleted_student_ids = set()

    def _lazy_delete_small_heap(self):
        while self._small_heap.values and self._small_heap.top in self._deleted_student_ids:
            self._deleted_student_ids.remove(self._small_heap.top)
            self._small_heap.pop()

    def add(self, student_id: int) -> None:
        if self.exists(student_id):
            return
        self._student_ids.add(student_id)
        if student_id in self._deleted_student_ids:
            # student_id之前需要删除，但是现在添加进来了就不用删了，小根堆保持不动
            self._deleted_student_ids.remove(student_id)
        else:
            # 之前不存在，现在将其入堆
            self._small_heap.push(student_id)

    def exists(self, student_id: int) -> bool:
        # in哈希表的时间复杂度是O(1)
        return student_id in self._student_ids

    def delete(self, student_id: int) -> bool:
        if not self.exists(student_id):
            return self.FAIL
        self._student_ids.remove(student_id)
        self._deleted_student_ids.add(student_id)
        self._lazy_delete_small_heap()
        return self.SUCCESS

    def random(self) -> Optional[int]:
        if not self._student_ids:
            return
        return secrets.choice(list(self._student_ids))

    def min(self) -> Optional[int]:
        self._lazy_delete_small_heap()
        return self._small_heap.top if self._small_heap.values else None


# 第二题：有⼀堆糖果，其数量为n，现将糖果分成不同数量的堆数（每堆数量均为整数，最少为
# 1），请算出糖果堆对应数量的最⼤乘积是多少，并给出对应的分配⽅案；
# 举例：糖果数量为8，可以得到的乘积最⼤为18，对应的分配⽅案为【2，3，3】；

"""思路：
利用数学导数求极值的方法，f(x)表示把n分成尽可能多的x的时候得到的最大的乘积，
得到f(x) = pow(x, n / x)，变形得到f(x) = exp(n * ln(x) / x), 由于n和自然底数e都是正数，
所有f(x)的单调性只与g(x) = ln(x) / x 有关, 对g(x)求导得到(1 - ln(x)) / pow(x, 2),
可知到x = e的时候f(x)取到极大值，由于x只能为整数所有x只有可能为2或者3，
将2和3带入g(x)可知当x=3的时候取最大，所有将n尽可能的分割成3相乘即可，但是有一种特殊情况要考虑比如4，分成2 * 2 > 1 * 3"""


def get_max_mult(n: int) -> int:
    if n <= 1:
        return 0
    if n == 2:
        return 1
    if n == 3:
        return 2
    num, mod = divmod(n, 3)
    if mod == 0:
        return pow(3, num)
    if mod == 1:
        # 特殊情况2 * 2 > 3 * 1
        return pow(3, num - 1) * 4
    return pow(3, num) * mod


# 第三题：6个⽔桶，其桶身和桶盖颜⾊相同：但6个桶颜⾊各不相同，求全部桶盖和桶身都不匹配的组合有多少
# 种？请把所有组合都打印出来；
"""思路：把6个盖子的全排列找出来，每一个排列的盖子和桶进行比较，保留桶和盖子都不匹配的排列"""


def print_bucket_combination(n: int) -> int:
    used = [False] * n
    combinations, combination = list(), list()

    def gen_combinations(i: int) -> None:
        if i == n:
            if all(k != combination[k] for k in range(n)):
                combinations.append(combination.copy())
            return
        for j in range(n):
            if used[j]:
                continue
            used[j] = True
            combination.append(j)
            gen_combinations(i + 1)
            used[j] = False
            combination.pop()

    gen_combinations(0)

    for comb in combinations:
        pprint({f"盖子-{comb[bucket]}": f"桶—{bucket}" for bucket in range(n)})
    return len(combinations)


print(print_bucket_combination(6))

# 第四题
# 假设需要设计⼀个承担百万级pv（⽤户总数1千万，每⽇⽤户⾏为⽇志数据预计1亿条）的电商⽹站登
# 录系统，你的服务器技术架构是怎么样的？⽤户信息的存储⽅案⼜会如何设计？如果由你来进⾏系统
# 整体技术负责，你会如何去把控整体开发进度和协调各⽅⾯资源?
"""思路：
    按照二八原则：总用户1千万，那么常在线的用户(uv)约有200万，由于只是个登录系统所以pv近似于等于uv=200万 * 4 = 800万，
    一天有24 * 0.2 = 4.8小时会有800 * 0.8 = 640万个请求，所以每秒有640万 / (4.8 * 60 * 60) = 370个请求，高峰时期的请求会是平时
    的3倍左右，370 * 3 = 1100个，一毫秒1个请求；
    产生以下问题：
        1. 以django作为后端来看单个web服务器每秒处理200个请求，那么为了应对高峰期至少得准备6个后端web服务器
        2. 服务器的session同步会耗费大量的内存和网络带宽
        3. 以mysql数据库为例，一秒处理1000多个请求事务压力巨大，服务会卡顿影响用户体验；日志数据量巨大，mysql无法直接分析用户行为
        4. 后端和数据库服务器要分开部署，服务器多，维护的工作量大
    针对以上问题，我将设计以下架构：
        负载均衡：使用负载均衡器Nginx来分发流量请求到各个服务器
        单点登录：redis集群的方式来存储session信息，一个用户登录的session过期时间设置在30分钟；
        读写分离：数据库采用读写分离的模式，根据用户的个人信息按照电话号码归属地进行分库，按照时间进行分表，这样平均下来每张表的用户数据会缩小到10万级别，减轻数据IO性能瓶颈；
        消息队列：使用kafka技术来削峰，当大量用户同时访问时先将请求的信息存到消息队列，让后直接返回给用户，后面消费者慢慢消费用户行为数据
        大数据集群：对于用户行为日志由于数据量太大，我们选择采用elasticsearch或者HDFS + Doris等分布式数据库技术来保存，可以无限的水平扩展数据分析能力
    
    分析团队各个成员的技能特长将团队成员分为技术型，沟通协作型；技术型按照领域分为前端开发，后端开发，运维，测试；本人负责代码检视和整体把控，
    组织沟通协作人员定期开会拉通各个技术人员，协调软件，硬件，信息安全各方面的资源；严格审视开发流程规范和代码质量，确保项目高度可自动化测试，项目
    健壮。
    
"""

# 第五题（选答加分项）
# 请在上述 4 道题中，选择其中⼀题，尝试⽤ ChatGPT 来解题，⽐较AI 代码和⾃⼰的代码的差异？说
# 出其中的优缺点，并给出如何借助 AI 提升开发效率的思路；
""" 选择第三题，以下是GPT给的答案

from itertools import permutations
# 定义桶身的颜色，桶盖颜色与桶身颜色相同
bucket_colors = ['red', 'green', 'blue', 'yellow', 'purple', 'orange']
# 生成所有可能的桶盖颜色组合
all_combinations = permutations(bucket_colors, 6)
# 过滤出满足条件的组合（桶盖和桶身颜色不同的组合）
valid_combinations = [combo for combo in all_combinations if sum(x == y for x, y in zip(combo, bucket_colors)) == 0]
# 打印所有满足条件的组合
for combo in valid_combinations:
    print(combo)
# 计算并打印组合的数量
print(f"总共有 {len(valid_combinations)} 种不匹配的组合。")

相比于我自己写的代码，AI利用了python标准库permutations来生成桶颜色的全排列，代码简洁可读性高，而且permutations底层是C语言实现，效率上肯定
是比我自己写的python回溯算法代码的执行效率要高，所以说见证了一点在python里面代码越简短运行效率越高；
通过以上AI生成的结果，使我进一步了解到能够利用python内置函数和标准库的时候要尽量利用，这样既可以提升开发效率又可以提升代码性能；
而且AI让我们开发人员很快找到自己开发过程中问题定位的方向，以及对编程知识的查漏补缺
"""
