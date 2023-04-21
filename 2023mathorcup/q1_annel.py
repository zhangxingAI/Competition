import numpy as np
from neal import SimulatedAnnealingSampler
import pandas as pd
import time
import random

# 载入数据
df = pd.read_csv('./附件1：data_100.csv')
data = df.values
# 定义参数
num_credit_cards = 100
num_thresholds = 10
interest_rate = 0.08  # 利息
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


# 使用neal库的SimulatedAnnealingSampler来解决QUBO问题
init = {i: 0 for i in range(1000)}
random_indices = random.sample(range(100), 1)
for i in range(1):
    init[random_indices[i] * 10] = 1


sampler = SimulatedAnnealingSampler()
response = sampler.sample_qubo(Q, num_reads=2000,initial_state = init)
# response = sampler.sample_qubo(Q)
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



