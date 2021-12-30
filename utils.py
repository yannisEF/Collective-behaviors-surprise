from tkinter import filedialog
import pickle
import datetime
import matplotlib.pyplot as plt


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


def read_csv_files(filenames, title="unnamed graph", xLabel="unnamed x-axis", yLabel="unnamed y-axis"):
    """
    Plots boxplots from a list of csv files
    """

    list_lines = []
    for filename in filenames:
        with open(filename, 'r') as f:
            rawlines = [line.replace("\n", "") for line in f.readlines()]
        
        list_lines.append([list(map(float, line.split(","))) for line in rawlines if len(line) != 0 and line[0] != "#"])
    
    # Compile data from multiple files and display boxplots
    if any([len(list_lines[0]) != len(lines) for lines in list_lines]):
        raise ValueError("All data files must have the same amount of data.")
    
    xData, yData = [], []
    for i in range(len(list_lines[0])):
        xData.append(list_lines[0][i][0])
        yData.append([other_file[i][1] for other_file in list_lines])


    # Create a figure instance
    fig, ax = plt.subplots(figsize=(9, 6))

    # plot data
    if len(yData[0]) == 1:
        ax.plot(xData, yData)
    else:
        ax.set_xticklabels(xData)
        ax.boxplot(yData)

    # Remove top axes and right axes ticks
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()

    ax.set_autoscale_on(True)

    # Add labels and title
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)

    plt.title(title if title not in ["", "unnamed graph"] else get_time_stamp())

    # Display
    plt.show()