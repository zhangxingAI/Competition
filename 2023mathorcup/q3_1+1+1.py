import numpy as np
import pandas as pd

interest_rate = 0.08

def final_income_2(t1, h1, t2, h2):
    total_pass_rate = t1 * t2
    total_bad_rate = (h1 + h2) / 2
    return interest_rate * total_pass_rate - (1 + interest_rate) * total_pass_rate * total_bad_rate

def final_income_3(t1, h1, t2, h2, t3, h3):
    total_pass_rate = t1 * t2 * t3
    total_bad_rate = (h1 + h2 + h3) / 3
    return interest_rate * total_pass_rate - (1 + interest_rate) * total_pass_rate * total_bad_rate

# 读取数据
df = pd.read_csv('./附件1：data_100.csv')
data = df.values

# 获取第一次选择的信用评分卡阈值
first_card = 48
first_threshold = 0
t1, h1 = data[first_threshold, 2 * first_card], data[first_threshold, 2 * first_card + 1]

# 获取第二次选择的信用评分卡阈值
max_income_2 = -np.inf
second_card, second_threshold = -1, -1

for card in range(100):
    if card == first_card:
        continue
    for threshold in range(10):
        t2, h2 = data[threshold, 2 * card], data[threshold, 2 * card + 1]
        income = final_income_2(t1, h1, t2, h2)
        if income > max_income_2:
            max_income_2 = income
            second_card, second_threshold = card, threshold

# 更新第一次选择的信用评分卡的通过率和坏账率
t1 *= data[second_threshold, 2 * second_card]
h1 = (h1 + data[second_threshold, 2 * second_card + 1]) / 2

# 获取第三次选择的信用评分卡阈值
max_income_3 = -np.inf
third_card, third_threshold = -1, -1

for card in range(100):
    if card == first_card or card == second_card:
        continue
    for threshold in range(10):
        t3, h3 = data[threshold, 2 * card], data[threshold, 2 * card + 1]
        income = final_income_3(t1, h1*2, t3, h3, 1, 0)
        if income > max_income_3:
            max_income_3 = income
            third_card, third_threshold = card, threshold

# 输出结果
print("从信用评分卡：{} 中选择阈值：{}，通过率：{}，坏账率：{}".format(first_card + 1, first_threshold + 1, data[first_threshold, 2 * first_card], data[first_threshold, 2 * first_card + 1]))
print("从信用评分卡：{} 中选择阈值：{}，通过率：{}，坏账率：{}".format(second_card + 1, second_threshold + 1, data[second_threshold, 2 * second_card], data[second_threshold, 2 * second_card + 1]))
print("从信用评分卡：{} 中选择阈值：{}，通过率：{}，坏账率：{}".format(third_card + 1, third_threshold + 1, data[third_threshold, 2 * third_card], data[third_threshold, 2 * third_card + 1]))

print("总通过率:", t1 * data[third_threshold, 2 * third_card])
print("总坏账率:", (h1*2 + data[third_threshold, 2 * third_card + 1]) / 3)
# print("总坏账率:", h1)

# 计算最终收入
final_income_value = final_income_3(data[first_threshold, 2 * first_card], data[first_threshold, 2 * first_card + 1],
                                  data[second_threshold, 2 * second_card], data[second_threshold, 2 * second_card + 1],
                                  data[third_threshold, 2 * third_card], data[third_threshold, 2 * third_card + 1])
print("最终收入:", final_income_value)
