import pandas as pd
import numpy as np
import time

# 载入数据
df = pd.read_csv('./附件1：data_100.csv')
data = df.iloc[:, :6].values

# 定义利息
interest_rate = 0.08


def final_income(t1, h1, t2, h2, t3, h3):
    total_pass_rate = t1 * t2 * t3
    total_bad_rate = (h1 + h2 + h3) / 3
    return interest_rate * total_pass_rate - (1 + interest_rate) * total_pass_rate * total_bad_rate

start_time = time.perf_counter()
# 穷举所有可能的阈值组合
max_income = -np.inf
best_combination = []

for i in range(10):
    for j in range(10):
        for k in range(10):
            t1, h1 = data[i, 0], data[i, 1]
            t2, h2 = data[j, 2], data[j, 3]
            t3, h3 = data[k, 4], data[k, 5]
            income = final_income(t1, h1, t2, h2, t3, h3)

            if income > max_income:
                max_income = income
                best_combination = [(i, t1, h1), (j, t2, h2), (k, t3, h3)]

# 计算运行时间
end_time = time.perf_counter()
run_time = (end_time - start_time) * 1000

# 输出结果
for idx, (threshold, pass_rate, bad_rate) in enumerate(best_combination):
    print(f"从信用评分卡： {idx + 1} 中选择阈值： {threshold+1}，通过率为 {pass_rate:.4f}，坏账率为 {bad_rate:.4f}")

# 计算总通过率和总坏账率
total_pass_rate = np.prod([pass_rate for _, pass_rate, _ in best_combination])
total_bad_debt_rate = np.mean([bad_rate for _, _, bad_rate in best_combination])

print("总通过率:", total_pass_rate)
print("总坏账率:", total_bad_debt_rate)

# 计算最终收入
final_income_value = final_income(
    *[value for _, pass_rate, bad_rate in best_combination for value in (pass_rate, bad_rate)])
print("最终收入:", final_income_value)
print("程序运行时间为: {:.2f}ms".format(run_time))
