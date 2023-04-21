import dwave.inspector
from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite
import numpy as np
import pandas as pd
import time
import random
# 载入数据
df = pd.read_csv('./附件1：data_100.csv')
data = df.values

num_credit_cards = 100
num_thresholds = 10
interest_rate = 0.08  # 利息
lagrange_multiplier = 1000  # 拉格朗日乘子
penalty = 100000  # 罚函数系数
start_time = time.perf_counter()

# 初始化QUBO字典
Q = {(i, j): 0 for i in range(1000) for j in range(1000)}

# 定义目标函数和约束条件
for card in range(num_credit_cards):
    for threshold in range(num_thresholds):
        i = card * num_thresholds + threshold
        t, h = data[threshold, 2 * card], data[threshold, 2 * card + 1]
        Q[(i, i)] = -(interest_rate * t - (1 + interest_rate) * t * h)

# 添加罚函数以确保只选择一个阈值
for i in range(1000):
    for j in range(i + 1, 1000):
        Q[(i, j)] += penalty


# 使用D-Wave量子计算求解器

init = {i: 0 for i in range(1000)}
# for i in random.sample(range(1000), 1):
init[500] = 1
anneal_schedule = [
    (0.0, 1.0),  # 在时间 0.0 时，温度为 1.0
    (100.0, 0.01),  # 在时间 100.0 时，温度为 0.1
    (200.0, 1.0)  # 在时间 200.0 时，温度为 1.0
]

dwave_sampler = DWaveSampler(token='DEV-af6776f9261ccb0543f97661a35da07b952ee527', endpoint='https://cloud.dwavesys.com/sapi')
sampler = EmbeddingComposite(dwave_sampler)
response = sampler.sample_qubo(Q, num_reads=200,initial_state = init,anneal_schedule=anneal_schedule)

# 获取最优解
best_solution = response.first.sample

# 计算运行时间
end_time = time.perf_counter()
run_time = (end_time - start_time) * 1000

# 输出最优解
print("Best solution:", best_solution)

# 输出结果
selected_thresholds = [i for i, value in best_solution.items() if value == 1]
for threshold in selected_thresholds:
    card = threshold // 10
    idx = threshold % 10
    print(f"从信用评分卡： {card + 1} 中选择阈值 ：{idx+1}，通过率为 {data[idx, 2 * card]:.4f}，"
          f"坏账率为 {data[idx, 2 * card + 1]:.4f},"
          f"总收入为 {(interest_rate * data[idx, 2 * card] - (1 + interest_rate) * data[idx, 2 * card] * data[idx, 2 * card + 1]):.4f}")
print("程序运行时间为: {:.2f}ms".format(run_time))