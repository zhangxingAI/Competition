import numpy as np
from neal import SimulatedAnnealingSampler
import pandas as pd

# 载入数据
df = pd.read_csv('./selected_t.csv')
data = df.values
# 定义参数

num_thresholds = 38
num_combinations = 8436
interest_rate = 0.08  # 利息
penalty = 100000  # 罚函数系数


# 定义目标函数
def final_income(t1, h1, t2, h2, t3, h3):
    total_pass_rate = t1 * t2 * t3
    total_bad_debt_rate = (h1 + h2 + h3) / 3
    final_income = interest_rate * total_pass_rate - (1 + interest_rate) * total_pass_rate * total_bad_debt_rate
    return final_income

# 初始化QUBO字典
Q = {(i, j): 0 for i in range(num_combinations) for j in range(num_combinations)}
combinations_list = list(combinations(range(num_thresholds), 3))

for i in range(num_combinations):
    for j in range(i, num_combinations):
        t1, h1 = data[combinations_list[i][0], 0], data[combinations_list[i][0], 1]
        t2, h2 = data[combinations_list[i][1], 2], data[combinations_list[i][1], 3]
        t3, h3 = data[combinations_list[i][2], 4], data[combinations_list[i][2], 5]
        income_j = final_income(t1, h1, t2, h2, t3, h3)
        Q[(i, j)] = -income_i

# 添加罚函数以确保只选择一个阈值
for i in range(num_combinations):
    for j in range(i + 1, num_combinations):
        Q[(i, j)] += penalty

# 使用neal库的SimulatedAnnealingSampler来解决QUBO问题

sampler = SimulatedAnnealingSampler()
response = sampler.sample_qubo(Q, num_reads=2000)

# 获取最优解
best_solution = response.first.sample

# 输出最优解
print("Best solution:", best_solution)

# 输出结果
top_solution = sampleset.first.sample
selected_combination = [i for i, value in top_solution.items() if value == 1][0]

selected_indices = combinations_list[selected_combination]
t1, h1 = data[selected_indices[0], 0], data[selected_indices[0], 1]
t2, h2 = data[selected_indices[1], 2], data[selected_indices[1], 3]
t3, h3 = data[selected_indices[2], 4], data[selected_indices[2], 5]

print(f"最优组合: 选择阈值 {selected_indices[0] + 1}，通过率为 {t1:.4f}，坏账率为 {h1:.4f}")
print(f"最优组合: 选择阈值 {selected_indices[1] + 1}，通过率为 {t2:.4f}，坏账率为 {h2:.4f}")
print(f"最优组合: 选择阈值 {selected_indices[2] + 1}，通过率为 {t3:.4f}，坏账率为 {h3:.4f}")

income_optimal = final_income(t1, h1, t2, h2, t3, h3)
print(f"最终收入: {income_optimal:.4f}")



