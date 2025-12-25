import numpy as np
from scipy.stats import ttest_ind, t

aff = np.loadtxt("welschAff.txt", delimiter=",").flatten()
naf = np.loadtxt("welschNAf.txt", delimiter=",").flatten()

t_stat, p_value = ttest_ind(aff, naf, equal_var=False)


mean_diff = np.mean(aff) - np.mean(naf)

se = np.sqrt(np.var(aff, ddof=1)/len(aff) + np.var(naf, ddof=1)/len(naf))

df = (np.var(aff, ddof=1)/len(aff) + np.var(naf, ddof=1)/len(naf))**2 / (
    (np.var(aff, ddof=1)/len(aff))**2/(len(aff)-1) +
    (np.var(naf, ddof=1)/len(naf))**2/(len(naf)-1)
)

alpha = 0.05
t_crit = t.ppf(1 - alpha/2, df)
ci_low = mean_diff - t_crit * se
ci_high = mean_diff + t_crit * se

print("Welch t-test result")
print("-------------------")
print(f"t-statistic: {t_stat}")
print(f"p-value:     {p_value}")
print(f"Mean diff:   {mean_diff}")
print(f"95% CI:      [{ci_low}, {ci_high}]")