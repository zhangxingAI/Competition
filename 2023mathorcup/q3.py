import pandas as pd
import numpy as np
from neal import SimulatedAnnealingSampler
from dimod import BinaryQuadraticModel
import itertools
import time

# 载入数据
df = pd.read_csv('./附件1：data_100.csv')
data = df.values

# 定义利息和罚款项
interest_rate = 0.08
penalty = 100000

# 定义目标函数和约束条件
def objective_function(x):
    # 计算最终收入
    total_pass_rate = 1
    total_bad_debt_rate = 0
    for i, value in enumerate(x):
        if value == 1:
            card_idx = i // 10
            threshold_idx = i % 10
            total_pass_rate *= data[threshold_idx, 2 * card_idx]
            total_bad_debt_rate += data[threshold_idx, 2 * card_idx + 1]
    total_bad_debt_rate /= 3
    final_income = interest_rate * total_pass_rate - (1 + interest_rate) * total_pass_rate * total_bad_debt_rate
    return final_income


start_time = time.perf_counter()

# 构建 QUBO 矩阵
Q = {(i, j): 0 for i in range(1000) for j in range(1000)}
print("程序运行时间为: {:.2f}ms".format(time.perf_counter()-start_time))

# 计算目标函数
for i, j in itertools.combinations(range(1000), 2):
    if i // 10 != j // 10:
        t1, h1 = data[i % 10, 2 * (i // 10)], data[i % 10, 2 * (i // 10) + 1]
        t2, h2 = data[j % 10, 2 * (j // 10)], data[j % 10, 2 * (j // 10) + 1]
        for k in range(1000):
            if k != i and k != j and k // 10 != i // 10 and k // 10 != j // 10:
                t3, h3 = data[k % 10, 2 * (k // 10)], data[k % 10, 2 * (k // 10) + 1]
                w = interest_rate * t1 * t2 * t3 - (1 + interest_rate) * (t1 * h1 + t2 * h2 + t3 * h3) / 3
                Q[(i, j)] -= w
                Q[(j, i)] -= w

# 添加约束条件
for i in range(1000):
    Q[(i, i)] -= penalty
    for j in range(i + 1, 1000):
        if i // 10 == j // 10:
            Q[(i, j)] += penalty
        else:
            Q[(i, j)] += 2 * penalty

bqm = BinaryQuadraticModel.from_qubo(Q, offset=0.0)
for i in range(10):
    bqm.add_linear_constraint([(i * 10 + j, 1) for j in range(10)], constant=3)
# 求解 QUBO 问题
sampler = SimulatedAnnealingSampler()
response = sampler.sample(bqm, num_reads=300)

end_time = time.perf_counter()
run_time = (end_time - start_time) * 1000

# 获取最优解
best_solution = response.first.sample
selected_thresholds = [i for i, value in best_solution.items() if value == 1]

# 输出结果
for threshold in selected_thresholds:
    card = threshold // 10
    idx = threshold % 10
    print(f"从信用评分卡： {card + 1} 中选择阈值 ：{idx+1}，通过率为 {data[idx, 2 * card]:.4f}，坏账率为 {data[idx, 2 * card + 1]:.4f}")
print("最终收入:", objective_function(best_solution))
print("程序运行时间为: {:.2f}ms".format(run_time))