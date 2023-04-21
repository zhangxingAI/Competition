import pandas as pd
import numpy as np

interest_rate = 0.08

def final_income(t1, h1, t2, h2, t3, h3):
    total_pass_rate = t1 * t2 * t3
    total_bad_rate = (h1 + h2 + h3) / 3
    return interest_rate * total_pass_rate - (1 + interest_rate) * total_pass_rate * total_bad_rate

# 读取数据
df = pd.read_csv('./附件1：data_100.csv')
data = df.values

max_income = -np.inf
best_cards = []
best_thresholds = []

# 穷举法
for card1 in range(100):
    for threshold1 in range(10):
        t1, h1 = data[threshold1, 2 * card1], data[threshold1, 2 * card1 + 1]
        for card2 in range(card1 + 1, 100):
            for threshold2 in range(10):
                t2, h2 = data[threshold2, 2 * card2], data[threshold2, 2 * card2 + 1]
                for card3 in range(card2 + 1, 100):
                    for threshold3 in range(10):
                        t3, h3 = data[threshold3, 2 * card3], data[threshold3, 2 * card3 + 1]
                        income = final_income(t1, h1, t2, h2, t3, h3)
                        if income > max_income:
                            max_income = income
                            best_cards = [card1, card2, card3]
                            best_thresholds = [threshold1, threshold2, threshold3]


for i in range(3):

    print("从信用评分卡：{}中选择阈值：{}，通过率：{}，坏账率：{}".format(best_cards[i] + 1, best_thresholds[i] + 1, data[best_thresholds[i], 2 * best_cards[i]], data[best_thresholds[i], 2 * best_cards[i] + 1]))
# 计算总通过率和总坏账率
total_pass_rate = data[best_thresholds[0], 2 * best_cards[0]] * data[best_thresholds[1], 2 * best_cards[1]] * data[best_thresholds[2], 2 * best_cards[2]]
total_bad_debt_rate = (data[best_thresholds[0], 2 * best_cards[0] + 1] + data[best_thresholds[1], 2 * best_cards[1] + 1] + data[best_thresholds[2], 2 * best_cards[2] + 1]) / 3

print("总通过率:", total_pass_rate)
print("总坏账率:", total_bad_debt_rate)

print("最终收入:", max_income)
