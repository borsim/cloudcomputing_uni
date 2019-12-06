import sys
import numpy as np


# Usage: command line arguments of difficulty bits, expected runtime and confidence bound as args 1, 2 and 3
diff_b = 24
confidence = 0.6
num_expected_hashes = 2 ** diff_b
if len(sys.argv) - 1 == 3:
    diff_b = int(sys.argv[1])
    runtime = float(sys.argv[2])
    confidence = float(sys.argv[3])

p = np.float64(1 / (2 ** diff_b))
one_minus_p = np.float64(1.0 - p)
prob_not_yet = np.float64(one_minus_p)
num_trials_to_confidence = 0
step = 1000

while (1 - prob_not_yet) < confidence:
    prob_not_yet = np.float64(prob_not_yet * np.power(one_minus_p, step))
    # if (num_trials_to_confidence % 100000 == 0):
    #     print("1 - current_prob: ", prob_not_yet, " , 1-confidence: ", (1-confidence))
    num_trials_to_confidence += step

safety_margin = num_trials_to_confidence / num_expected_hashes
totalhashes = (safety_margin * num_expected_hashes)
timetaken = totalhashes / 374381
numvms = int(np.ceil(timetaken / runtime))
print("With the given difficulty bits, runtime and confidence your safety margin ratio is: ", safety_margin, ", using ", numvms, " VMs.")