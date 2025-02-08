import pickle
import pprint

from rouge import Rouge

from utils.cer import calculateCERMatch

with open('../output/output.pth', 'rb') as f:
    tot_output = pickle.load(f)
with open('../output/ref.pth', 'rb') as f:
    tot_ref = pickle.load(f)

pprint.pprint(Rouge().get_scores(
    hyps=tot_output,
    refs=tot_ref,
    avg=True,
    ignore_empty=True
))

avg_result = 0
n = len(tot_output)

from jiwer import cer

for i in range(len(tot_output)):
    # if len(tot_output[i]) < 1:
    #     n -= 1
    #     continue
    result = cer(
        hypothesis=tot_output[i], reference=tot_ref[i]
    )
    avg_result += result

print(f'normed edit distance: {avg_result / n}')

# print(cer_avg(tot_ref, tot_output, sep=' '))
# print(cer_avg(tot_ref, tot_output))
