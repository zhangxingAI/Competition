import pandas as pd
import numpy as np
from itertools import combinations
from dimod import BinaryQuadraticModel
from neal import SimulatedAnnealingSampler

# 载入数据
df = pd.read_csv('./附件1：data_100.csv')
data = df.values

def final_income(t1, h1, t2, h2):
    interest_rate = 0.08
    total_pass_rate = t1 * t2
    total_bad_rate = (h1 + h2) / 2
    return interest_rate * total_pass_rate - (1 + interest_rate) * total_pass_rate * total_bad_rate

# 创建Q矩阵
num_credit_cards = 100
num_thresholds = 10
penalty = 100000  # 罚函数系数
Q = {(i, j): 0 for i in range(1000) for j in range(1000)}

for i, j in combinations(range(num_credit_cards * num_thresholds), 2):
    if i // num_thresholds != j // num_thresholds:
        t1, h1 = data[i % num_thresholds, 2 * (i // num_thresholds)], data[i % num_thresholds, 2 * (i // num_thresholds) + 1]
        t2, h2 = data[j % num_thresholds, 2 * (j // num_thresholds)], data[j % num_thresholds, 2 * (j // num_thresholds) + 1]
        Q[(i, j)] = -final_income(t1, h1, t2, h2)

for i in range(100):
    for j in range(10):
        for k in range(j + 1, 10):
            Q[(i * 10 + j, i * 10 + k)] += penalty

for i in range(1000):
    Q[(i, i)] -= 2 * penalty
    for j in range(i + 1, 1000):
        Q[(i, j)] += penalty
        Q[(j, i)] += penalty
# 使用SimulatedAnnealingSampler求解QUBO问题
bqm = BinaryQuadraticModel.from_qubo(Q)
sampler = SimulatedAnnealingSampler()
sampleset = sampler.sample(bqm, num_reads=2000)

# 输出结果
top_solutions = sorted(sampleset.data(), key=lambda x: x.energy)[:10]
print(top_solutions)
for idx, solution in enumerate(top_solutions):
    sample = solution.sample
    selected_indices = [i for i, value in sample.items() if value == 1]
    t1, h1 = data[selected_indices[0] % num_thresholds, 2 * (selected_indices[0] // num_thresholds)], data[selected_indices[0] % num_thresholds, 2 * (selected_indices[0] // num_thresholds) + 1]
    t2, h2 = data[selected_indices[1] % num_thresholds, 2 * (selected_indices[1] // num_thresholds)], data[selected_indices[1] % num_thresholds, 2 * (selected_indices[1] // num_thresholds) + 1]
    print(f"组合 {idx + 1}: 从信用评分卡 {selected_indices[0] // num_thresholds + 1} 中选择阈值 {selected_indices[0] % num_thresholds + 1}，通过率为 {t1:.4f}，坏账率为 {h1:.4f}。从信用评分卡 {selected_indices[1] // num_thresholds + 1} 中选择阈值 {selected_indices[1] % num_thresholds + 1}，通过率为 {t2:.4f}，坏账率为 {h2:.4f}。收入为 {final_income(t1, h1, t2, h2)}")