
def reverse_dict_with_repeat(A_dict:dict):
    """
    Reverses a dictionnary, values that appear several times are casted into a list
    """
    new_dict = {}

    for key, value in A_dict:
        if key in new_dict is True:
            new_dict[key].append(value)
        else:
            new_dict[key] = [value]
    
    return new_dict
