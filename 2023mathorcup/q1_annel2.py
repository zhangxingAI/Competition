import numpy as np
import pandas as pd
from neal import SimulatedAnnealingSampler
from dimod import BinaryQuadraticModel

# 载入数据
df = pd.read_csv('./附件1：data_100.csv')

# 定义参数
n = 100  # 信用评分卡数量
m = 10  # 每个信用评分卡的通过率与坏账率组合数量
interest_rate = 0.08  # 利息
lagrange_multiplier = 10  # 拉格朗日乘子

# 随机生成一个200列10行的矩阵，代表100个信用评分卡的通过率和坏账率
data = df.values

# 初始化QUBO字典
Q = {}

# 构建QUBO字典
for card in range(n):
    for threshold in range(m):
        t = data[threshold, 2 * card]
        h = data[threshold, 2 * card + 1]
        income = interest_rate * t - (1 + interest_rate) * t * h

        Q[(card * 10 + threshold, card * 10 + threshold)] = -income + lagrange_multiplier
        for other_threshold in range(threshold + 1, 10):
            Q[(card * 10 + threshold, card * 10 + other_threshold)] = 2 * lagrange_multiplier

for card_1 in range(n):
    for card_2 in range(card_1 + 1, n):
        for threshold_1 in range(m):
            for threshold_2 in range(m):
                Q[(card_1 * 10 + threshold_1, card_2 * 10 + threshold_2)] = 2 * lagrange_multiplier

# 构建二次规划模型
bqm = BinaryQuadraticModel.from_qubo(Q, offset=0.0)

# 求解QUBO问题
sampler = SimulatedAnnealingSampler()
response = sampler.sample(bqm, num_reads=30000)

# 获取最优解
best_solution = response.first.sample

# 输出结果
selected_thresholds = [i for i, value in best_solution.items() if value == 1]

if not selected_thresholds:
    print("未找到符合条件的解，请尝试调整拉格朗日乘子或增加num_reads的值。")
else:
    selected_threshold = selected_thresholds[0]
    selected_card = selected_threshold // 10
    selected_threshold_index = selected_threshold % 10
    print(f"从信用评分卡 {selected_card + 1} 中选择阈值 {selected_threshold_index + 1}，通过率为 {data[selected_threshold_index, 2 * selected_card]:.4f}，坏账率为 {data[selected_threshold_index, 2 * selected_card + 1]:.4f}")

# 计算最终收入
final_income = interest_rate * data[selected_threshold_index, 2 * selected_card] - (1 + interest_rate) * data[selected_threshold_index, 2 * selected_card] * data[selected_threshold_index, 2 * selected_card + 1]
print("最终收入:", final_income)
