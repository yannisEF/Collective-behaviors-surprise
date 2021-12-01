
def reverse_dict_with_repeat(A_dict:dict):
    """
    Reverses a dictionnary, values that appear several times are casted into a list
    """
    new_dict = {}

    for key, value in A_dict.items():
        if value in new_dict:
            new_dict[value].append(key)
        else:
            new_dict[value] = [key]
    
    return new_dict
