import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.timesplit import RollingSplit, ExpandingSplit
import numpy as np

# Dummy dataset
data = np.arange(10)

# Initialize your rolling split
splitter = RollingSplit(train_size=3, test_size=2, step_size=2)

# Loop through splits and print
for train_idx, test_idx in splitter.split(data):
    print("-" * 40)
    print("Rolling Split - Train:", train_idx, "Test:", test_idx)

print("=" * 40)
splitter = ExpandingSplit(test_size=2, step_size=2)

# Loop through splits and print
for train_idx, test_idx in splitter.split(data):
    print("-" * 40)
    print("Expanding Split - Train:", train_idx, "Test:", test_idx)
