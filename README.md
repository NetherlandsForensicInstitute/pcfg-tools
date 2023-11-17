# pcfg-tools
Collection of tools for modifying PCFG Rulesets

## merge_rules.py
PCFG Merge Rules is an open-source Python program that allows you to merge Probabilistic Context-Free Grammar (PCFG) rule sets based on the [pcfg_cracker](https://github.com/lakiw/pcfg_cracker).

### Description
PCFG Merge Rules simplifies the process of merging two PCFG rule sets, allowing you to create a new rule set by combining a generic set of rules with an input set. You can also adjust the weight of the input set when merging to control the influence of each set on the final rule set.

### Requirements
🐍 Python 3.x

### Usage
Run the script from the command line with the necessary arguments. Here is the basic syntax:
```
python merge_rules.py --rule [GENERIC_RULE_PATH] --input [INPUT_RULE_PATH] --output [OUTPUT_RULE_PATH] --weight [WEIGHT]
```

 * `GENERIC_RULE_PATH`: Path to the generic rule set.
 * `INPUT_RULE_PATH`: Path to the input rule set to be merged.
 * `OUTPUT_RULE_PATH`: Path where the merged rule set will be saved.
 * `WEIGHT`: Numerical weight (0-1) to balance the importance of the input rule set in the merge.


Optional arguments:
 * `--replace_alphas_only`: If set, only alpha structures from the input will be merged.

### Credits
This tool is based on the work of Shiva Houshmand and Aggarwal Sudhir. And is only useful with [pcfg_cracker](https://github.com/lakiw/pcfg_cracker) created by Matt Weir.
