from tkinter import filedialog

import pickle
import datetime
import matplotlib.pyplot as plt
import numpy as np


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


def check_selected(func):
    """
    Decorator to check if at least one csv file is selected in a listbox
    """

    def inner(*args, **kwargs):
        res = None
        try:
            res = func(*args, **kwargs)
        except IndexError:
            print("Please select at least one file.")
        except Exception as e:
            print(e)
            pass

        return res
    return inner


def get_time_stamp():
    return datetime.datetime.now().strftime("%Y%m%d_%H%M")


def read_csv_files(filename, offset=-1, title="unnamed graph", xLabel="unnamed x-axis", yLabel="unnamed y-axis", logscale=True):
    """
    Plots boxplots from a list of csv files
    """

    with open(filename, 'r') as f:
        rawlines = [line.replace("\n", "") for line in f.readlines()]
    
    lines = [tuple(map(float, line.split(","))) for line in rawlines if len(line) != 0 and line[0] != "#"]
    
    xData, yData = [], []
    for line in lines:
        xData.append(line[0])
        yData.append(line[1])

    data = {}
    for i in range(len(xData)):
        if int(xData[i]) not in data:
            data[int(xData[i])] = []

        data[int(xData[i])].append(yData[i])

    # Create a figure instance
    fig, ax = plt.subplots(figsize=(9, 6))

    # plot data
    ax.boxplot(list(data.values()), positions=list(data.keys()))

    # Remove top axes and right axes ticks
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()

    ax.set_autoscale_on(True)
    if logscale is True:
        plt.yscale("log")

    # Add labels and title
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)

    plt.title(title if title not in ["", "unnamed graph"] else get_time_stamp())

    # Display
    plt.show()


def entropy(prob):
    """
    Computes the entropy of the given probability
    """

    if prob <= 0 or prob >= 1:  return 0
    return -prob * np.log2(prob) - (1 - prob) * np.log2(1 - prob)