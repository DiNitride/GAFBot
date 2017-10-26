
def merge_dicts(base_dict, merge_dict):
    base_dict = base_dict.copy()
    # print("Merging dicts!")
    # print(f"Base dict: {base_dict}")
    # print(f"Merging dict: {merge_dict}")
    for value in merge_dict:
        # print(f"Key: {value}")
        if isinstance(merge_dict[value], dict):
            # print("Value is dict")

            if value not in base_dict.keys():
                base_dict[value] = {}
                # print(f"Base did not have value {value} so created key with empty dict")
            # print(f"Merging {merge_dict[value]} into {base_dict[value]}")
            base_dict[value] = merge_dicts(base_dict[value], merge_dict[value])
        else:
            base_dict[value] = merge_dict[value]

    return base_dict
