import os
import json
import matplotlib.pyplot as plt
import datetime
import pytz
import numpy as np
from scipy import stats


x = []
y = []
for f in os.listdir("test_results"):
    with open(f"test_results/{f}", "r") as fp:
        obj = json.load(fp)
        score = (10000/9) * obj["correct"]/(80 + obj["used_time"])
        y.append(score)
        x.append(int(f.split("_")[1]))

sorted_pairs = sorted(zip(x, y))
x, y = zip(*sorted_pairs)

x = [pytz.timezone('Pacific/Auckland').fromutc(datetime.datetime.utcfromtimestamp(k)) for k in x]


pre_exp = y[:11]
during_exp = y[11:33] # Should be 11:33
post_exp = y[33:] # Should be 33:

def test(y1, y2):
    pt = round(stats.ttest_ind(y1, y2, equal_var=False)[1], 20)
    pw = round(stats.mannwhitneyu(y1, y2)[1], 20)
    print(f"Two sample t-test (independent smples) p-val: {pt} ({'significant' if pt < 0.05 else 'not significant'})")
    print(f"Mann-Whitney U Test p-val: {pw} ({'significant' if pw < 0.05 else 'not significant'})")

print("\nPre and during experiment: ")
test(pre_exp, during_exp)

print("\nDuring and post experiment: ")
test(during_exp, post_exp)

print("\nPre and post experiment: ")
test(pre_exp, post_exp)
print("\n")

pre_exp_mean = np.mean(pre_exp)
during_exp_mean = np.mean(during_exp)
post_exp_mean = np.mean(post_exp)
print(f"Mean score pre experiment: {np.round(pre_exp_mean, 1)} (n={len(pre_exp)}) \nMean score during experiment: {np.round(during_exp_mean, 1)} (n={len(during_exp)}) \nMean score post experiment: {round(post_exp_mean, 1)} (n={len(post_exp)})")

plt.figure(figsize=(11, 6))

plt.axvline(x=x[10] - datetime.timedelta(hours=4), color='r', linestyle='--', label='Intervention starts')
plt.annotate('Intervention starts', (x[10] - datetime.timedelta(hours=15), y[10] + 5), textcoords="offset points", xytext=(-10,10), ha='center', color='red')

plt.axvline(x=x[11] + datetime.timedelta(hours=12), color='g', linestyle='--', label='Effects Expected')
plt.annotate('Effects Expected', (x[11] + datetime.timedelta(hours=2), y[11] + 9), textcoords="offset points", xytext=(-10,10), ha='center', color='green')

plt.axvline(x=x[19] - datetime.timedelta(hours=4), color='grey', linestyle='--', label='NY Break Starts')
plt.annotate('NY Break Start', (x[19] - datetime.timedelta(hours=26), y[19] - 6), textcoords="offset points", xytext=(-10,10), ha='center', color='grey')

plt.axvline(x=x[21] - datetime.timedelta(hours=4), color='grey', linestyle='--', label='NY Break Ends')
plt.annotate('NY Break end', (x[21] - datetime.timedelta(hours=26), y[21] + 5), textcoords="offset points", xytext=(-10,10), ha='center', color='grey')

plt.axvline(x=x[32], color='r', linestyle='--', label='Experiment Stops')
plt.annotate('Experiment Stops', (x[32], y[32] + 5), textcoords="offset points", xytext=(-10,10), ha='center', color='red')

plt.plot(x, y, marker='o', color='b', linestyle='-', linewidth=2, markersize=8)
plt.title('Plot of y-values against x-values')
plt.xlabel('Datetime')
plt.ylabel('Score (min 0, max 100)')
plt.grid(True)
plt.tight_layout()

# Show the plot
plt.show()