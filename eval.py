import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import linregress

input_path = "/path/to/InternVL3_14B_nframes64.jsonl"

with open(input_path, "r", encoding="utf-8") as f:
    data = [json.loads(line) for line in f]

triplets = []
temp = []
for item in data:
    temp.append(item)
    if len(temp) == 3:
        triplets.append(temp)
        temp = []

# 统计结果
records = []
aspect_stats = {} 
inacc_count = 0
outacc_count = 0

def format_answer(answer):
    """格式化答案，去除多余空格并转换为小写"""
    if "yes" in answer.lower():
        return "yes"
    elif "no" in answer.lower():
        return "no"


for group in triplets:
    part_nums = group[0]["part_nums"]
    aspect = group[0]["aspect"]
    
    ref_answers = {item["caption_type"]: format_answer(item["ref_answer"]) for item in group}
    model_answers = {item["caption_type"]: format_answer(item["model_response"]) for item in group}

    inacc = 1 if model_answers["in_video"] == ref_answers["in_video"] and model_answers["ground_truth"] == ref_answers["ground_truth"] else 0
    outacc = 1 if model_answers["out_video"] == ref_answers["out_video"] and model_answers["ground_truth"] == ref_answers["ground_truth"] else 0

    inacc_count += inacc
    outacc_count += outacc

    if aspect not in aspect_stats:
        aspect_stats[aspect] = {"in_correct": 0, "out_correct": 0, "total": 0}
    aspect_stats[aspect]["in_correct"] += inacc
    aspect_stats[aspect]["out_correct"] += outacc
    aspect_stats[aspect]["total"] += 1

    records.append({
        "part_nums": part_nums,
        "aspect": aspect,
        "inaccuracy": inacc,
        "outaccuracy": outacc,
        "outacc_minus_inacc": outacc - inacc
    })

df = pd.DataFrame(records)

# === 总体统计 ===
total_triplets = len(triplets)
overall_inacc = inacc_count / total_triplets
overall_outacc = outacc_count / total_triplets

print("=== Overall Accuracy Stats ===")
print(f"🔻 Total triplets: {total_triplets}")
print(f"✅ Inaccuracy (in_video): {overall_inacc*100:.2f}")
print(f"✅ Outaccuracy (out_video): {overall_outacc*100:.2f}")
print(f"✅ SAH Ratio: {((overall_outacc-overall_inacc)/(1-overall_inacc)*100):.2f}")
# === 每个 aspect 的正确率 ===
print("=== Accuracy by Aspect ===")
aspect_summary = []
for aspect, stats in aspect_stats.items():
    in_acc = stats["in_correct"] / stats["total"]
    out_acc = stats["out_correct"] / stats["total"]
    aspect_summary.append({
        "aspect": aspect,
        "in_video_accuracy": round(in_acc*100, 3),
        "out_video_accuracy": round(out_acc*100, 3),
        "difference": round((out_acc - in_acc)*100, 3),
        "total": stats["total"]
    })

aspect_df = pd.DataFrame(aspect_summary)
print(aspect_df)
