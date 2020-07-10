import seaborn as sns
import numpy as np
import matplotlib.pyplot as PLOT
import pytorch

import tensorflow as tf
np.random.seed(0)
sns.set()
uniform_data = np.random.rand(10, 12)
# ax = sns.heatmap(uniform_data)
flights = sns.load_dataset("flights")
flights = flights.pivot("month", "year", "passengers")
ax = sns.heatmap(flights, annot=True, fmt="d")
PLOT.show()
