import pandas as pd
# 载入数据
df = pd.read_csv('./附件1：data_100.csv')
data = df.values
num_credit_cards = 100
num_thresholds = 10
interest_rate = 0.08  # 利息
newdf = pd.DataFrame(index=range(num_thresholds), columns=range(num_credit_cards))

for card in range(num_credit_cards):
    for threshold in range(num_thresholds):
        t, h = data[threshold, 2 * card], data[threshold, 2 * card + 1]
        newdf.loc[threshold, card] = interest_rate * t - (1 + interest_rate) * t * h
newdf.to_csv("new.csv", index=False)


