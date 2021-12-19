from tkinter import filedialog
import pickle



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

def save_file(obj_saved):
    """
    Saves an object into a file
    """

    path_to_save = filedialog.asksaveasfilename(defaultextension=".pkl", filetypes=[("pickle files", "*.pkl")])
    
    try:
        with open(path_to_save, "wb") as f:
                pickle.dump(obj_saved, f)
        return "saved"
    except FileNotFoundError:
        return "not saved"

def load_file():
    """
    Loads a file and return its content
    """

    path_to_load = filedialog.askopenfilename(defaultextension=".pkl", filetypes=[("pickle files", "*.pkl")])

    try:
        with open(path_to_load, "rb") as f:
            return path_to_load.split("/")[-1].split(".")[0], pickle.load(f)
    except FileNotFoundError:
        return None, None