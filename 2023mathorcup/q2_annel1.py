
import pandas as pd
import numpy as np
from neal import SimulatedAnnealingSampler
from dimod import BinaryQuadraticModel
from itertools import product
from itertools import combinations
import itertools
import time
import random

# 载入数据
df = pd.read_csv('./附件1：data_100.csv')
data = df.iloc[:, :6].values

# 定义利息
interest_rate = 0.08
penalty = 100000
def final_income(t1, h1, t2, h2, t3, h3):
    total_pass_rate = t1 * t2 * t3
    total_bad_rate = (h1 + h2 + h3) / 3
    return interest_rate * total_pass_rate - (1 + interest_rate) * total_pass_rate * total_bad_rate

start_time = time.perf_counter()

# 构建QUBO
Q = {(i, j): 0 for i in range(30) for j in range(30)}

for i, j in product(range(30), repeat=2):
    card_i = i // 10
    card_j = j // 10

    if i == j:
        t = data[i % 10, 2 * card_i]
        h = data[i % 10, 2 * card_i + 1]
        Q[(i, j)] = -final_income(t, h, t, h, t, h)
    elif card_i != card_j:
        card1_i, card1_j = i % 10, j % 10
        t1, h1 = data[card1_i, 2 * card_i], data[card1_i, 2 * card_i + 1]
        t2, h2 = data[card1_j, 2 * card_j], data[card1_j, 2 * card_j + 1]

        for k in range(10):
            card3 = 3 - card_i - card_j
            t3, h3 = data[k, 2 * card3], data[k, 2 * card3 + 1]
            Q[(i, j)] = -final_income(t1, h1, t2, h2, t3, h3)

# 添加约束以确保每个信用评分卡只选择一个阈值
for i in range(3):
    for j in range(10):
        for k in range(j + 1, 10):
            Q[(i * 10 + j, i * 10 + k)] += penalty
print(Q)
bqm = BinaryQuadraticModel.from_qubo(Q, offset=0.0)

# 求解QUBO问题

init = {i: 0 for i in range(30)}
random_indices = random.sample(range(3), 3)
for i in range(3):
    init[random_indices[i] * 10] = 1

sampler = SimulatedAnnealingSampler()
# response = sampler.sample(bqm, num_reads=400,initial_state = init)
response = sampler.sample(bqm, num_reads=300)

# 获取最优解
best_solution = response.first.sample
print(best_solution)

# 计算运行时间
end_time = time.perf_counter()
run_time = (end_time - start_time) * 1000

# 输出结果
selected_thresholds = [i for i, value in best_solution.items() if value == 1]
for threshold in selected_thresholds:
    card = threshold // 10
    idx = threshold % 10
    print(f"从信用评分卡： {card + 1} 中选择阈值 ：{idx+1}，通过率为 {data[idx, 2 * card]:.4f}，坏账率为 {data[idx, 2 * card + 1]:.4f}")

sample = best_solution
# 计算总通过率和总坏账率
total_pass_rate = 1
total_bad_debt_rate = 0

for i, value in sample.items():
    if value == 1:
        card_idx = i // 10
        threshold_idx = i % 10
        total_pass_rate *= data[threshold_idx, 2 * card_idx]
        total_bad_debt_rate += data[threshold_idx, 2 * card_idx + 1]

total_bad_debt_rate /= 3

# 计算最终收入
final_income = interest_rate * total_pass_rate - (1 + interest_rate) * total_pass_rate * total_bad_debt_rate
print("最终收入:", final_income)
print("程序运行时间为: {:.2f}ms".format(run_time))



