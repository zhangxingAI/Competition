import pandas as pd
import numpy as np
import time
interest_rate = 0.08

def final_income(t1, h1):
    return interest_rate * t1 - (1 + interest_rate) * t1 * h1

# 读取数据
df = pd.read_csv('./附件1：data_100.csv')
data = df.values

max_income = -np.inf
best_card = -1
best_threshold = -1

start_time = time.perf_counter()
# 穷举法
for card in range(100):
    for threshold in range(10):
        t = data[threshold, 2 * card]
        h = data[threshold, 2 * card + 1]
        income = final_income(t, h)
        if income > max_income:
            max_income = income
            best_card = card
            best_threshold = threshold
# 计算运行时间
end_time = time.perf_counter()
run_time = (end_time - start_time) * 1000

print("从信用评分卡：{} 中选择阈值：{}，通过率：{}，坏账率：{}".format(best_card + 1, best_threshold + 1,
                                            data[best_threshold, 2 * best_card],
                                            data[best_threshold, 2 * best_card + 1]))
print("最终收入:", max_income)
print("程序运行时间为: {:.2f}ms".format(run_time))