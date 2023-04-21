import pandas as pd
import numpy as np
from itertools import combinations
from dimod import BinaryQuadraticModel
from neal import SimulatedAnnealingSampler
import itertools
import time

# 载入数据
df = pd.read_csv('./附件1：data_100.csv')
data = df.values

# 定义利息和罚款项
interest_rate = 0.08
penalty = 100000
num_credit_cards = 100
num_thresholds = 10

# 定义最终收入计算函数
def final_income(t1, h1, t2, h2, t3, h3):
    interest_rate = 0.08
    total_pass_rate = t1 * t2 * t3
    total_bad_rate = (h1 + h2 + h3) / 3
    return interest_rate * total_pass_rate - (1 + interest_rate) * total_pass_rate * total_bad_rate



start_time = time.perf_counter()

# 构建 QUBO 矩阵
Q = {(i, j): 0 for i in range(1000) for j in range(1000)}
print("程序运行时间为: {:.2f}ms".format(time.perf_counter()-start_time))

# 计算目标函数
for i, j, k in combinations(range(num_credit_cards * num_thresholds), 3):
    if i // num_thresholds != j // num_thresholds and i // num_thresholds != k // num_thresholds and j // num_thresholds != k // num_thresholds:
        t1, h1 = data[i % num_thresholds, 2 * (i // num_thresholds)], data[i % num_thresholds, 2 * (i // num_thresholds) + 1]
        t2, h2 = data[j % num_thresholds, 2 * (j // num_thresholds)], data[j % num_thresholds, 2 * (j // num_thresholds) + 1]
        t3, h3 = data[k % num_thresholds, 2 * (k // num_thresholds)], data[k % num_thresholds, 2 * (k // num_thresholds) + 1]
        w = final_income(t1, h1, t2, h2, t3, h3)
        Q[(i, j)] -= w
        Q[(i, k)] -= w
        Q[(j, k)] -= w
# 添加约束条件
# for card_idx in range(num_credit_cards):
#     indices = [card_idx * num_thresholds + i for i in range(num_thresholds)]
#     for i, j in combinations(indices, 2):
#         Q[(i, j)] += penalty
#         Q[(j, i)] += penalty
#     for i in indices:
#         Q[(i, i)] -= 2 * penalty
for i in range(100):
    for j in range(10):
        for k in range(j + 1, 10):
            Q[(i * 10 + j, i * 10 + k)] += penalty

# 添加约束条件
bqm = BinaryQuadraticModel.from_qubo(Q)
for i in range(100):
    bqm.add_linear_equality_constraint([(i * 10 + j, 1) for j in range(10)], constant=1, lagrange_multiplier=penalty)

bqm.add_linear_equality_constraint([(i, 1) for i in range(1000)], constant=3, lagrange_multiplier=penalty)

# 使用SimulatedAnnealingSampler求解QUBO问题
sampler = SimulatedAnnealingSampler()
sampleset = sampler.sample(bqm, num_reads=1000)


# 求解 QUBO 问题
sampler = SimulatedAnnealingSampler()
response = sampler.sample(bqm, num_reads=400)

end_time = time.perf_counter()
run_time = (end_time - start_time) * 1000

# 获取最优解
best_solution = response.first.sample
selected_thresholds = [i for i, value in best_solution.items() if value == 1]

t1, h1 = data[selected_thresholds[0] % num_thresholds, 2 * (selected_thresholds[0] // num_thresholds)], data[selected_thresholds[0] % num_thresholds, 2 * (selected_thresholds[0] // num_thresholds) + 1]
t2, h2 = data[selected_thresholds[1] % num_thresholds, 2 * (selected_thresholds[1] // num_thresholds)], data[selected_thresholds[1] % num_thresholds, 2 * (selected_thresholds[1] // num_thresholds) + 1]
t3, h3 = data[selected_thresholds[2] % num_thresholds, 2 * (selected_thresholds[2] // num_thresholds)], data[selected_thresholds[2] % num_thresholds, 2 * (selected_thresholds[2] // num_thresholds) + 1]


# 输出结果
for threshold in selected_thresholds:
    card = threshold // 10
    idx = threshold % 10
    print(f"从信用评分卡： {card + 1} 中选择阈值 ：{idx+1}，通过率为 {data[idx, 2 * card]:.4f}，坏账率为 {data[idx, 2 * card + 1]:.4f}")
print("最终收入:", final_income(t1, h1, t2, h2, t3, h3))
print("程序运行时间为: {:.2f}ms".format(run_time))