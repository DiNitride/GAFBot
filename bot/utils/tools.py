

def merge_dicts(base_dict, merge_dict):
    base_dict = base_dict.copy()
    for value in merge_dict:
        if value == "roleStates":
            base_dict[value] = merge_dict[value]
        elif isinstance(merge_dict[value], dict):
            base_dict[value] = merge_dicts(base_dict[value], merge_dict[value])
        else:
            base_dict[value] = merge_dict[value]

    return base_dict
