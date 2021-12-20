from tkinter import filedialog
import pickle
import datetime
import matplotlib.pyplot as pl


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


def getContentFromFile(filename):
    fichier = open(filename)
    lines = fichier.readlines()
    fichier.close()
    return lines

def getLinesWithPrefix(lines, prefix, removePrefix = False):
    retLines = []
    for l in lines:
        if l[0:len(prefix)] == prefix:
            if removePrefix == True:
                retLines.append(l[len(prefix):].replace("\n",""))
            else:
                retLines.append(l).replace("\n","")
    return retLines

def parseLinesToArrayOfValues ( rawlines ):
    lines = []
    for l in rawlines:
        if len(l) != 0 and l[0] != "#":
            l = l.split(",")
            l = map(float, l)
            lines.append(l)
    return lines

def getTimestamp():
    return datetime.datetime.now().strftime("%Y%m%d_%H%M")

def traceData(x, y, type="single", title="unnamed graph", xLabel="unnamed x-axis", yLabel="unnamed y-axis", xlimMin=-1, xlimMax=-1, ylimMin=-1, ylimMax=-1, legendLabel="", locLegend='upper right', autoscaling=True, outputFilename="empty"):
    
    # Create a figure instance
    fig = pl.figure(1, figsize=(9, 6))

    # Create an axes instance
    ax = fig.add_subplot(111)

    # plot data
    if type == "single":
        ax.plot(x, y)
    elif type == "multi":
        ax.boxplot(y)
        ax.set_xticklabels(x)
    
    # Remove top axes and right axes ticks
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()

    ax.set_autoscale_on(autoscaling)

    # Add labels and legend
    pl.xlabel(xLabel)
    pl.ylabel(yLabel)

    if title == "":
        pl.title(getTimestamp())
    else:
        pl.title(title)

    # Save the figure
    outputFilename = "graph_"+getTimestamp()+".pdf"
    
    fig.savefig(outputFilename, format="pdf", bbox_inches='tight')
    
    # Display
    pl.show() 

def read_csv_files(filenames):
    
    rawlines = []
    lines = []
    
    for i in range (len(filenames)):
        rawlines.append( getContentFromFile( filenames[i] ) )
        rawlines[i] = getLinesWithPrefix ( rawlines[i], "", True)
        lines.append( parseLinesToArrayOfValues( rawlines[i] ) )
    
    if len(filenames) == 1:
        # display raw data from one single file
        xData = []
        yData = []
        i = 0
        for l in lines[0]:
            l2 = list(l) # Python 3: map returns an iterator, you can only iterate over once
            if i % 1 == 0:
                xData.append( l2[0] )
                yData.append( l2[1] )
                print ( str(l2[0]) + "," + str(l2[1]) )
            i = i + 1
        traceData(xData, yData)
        
    else:
        
        # compile data from multiple files and display boxplots
        if len(lines)<5:
            print ("[ERROR] at least 5 data file are required to trace boxplots. Stop.")
            quit()
        
        for i in range (1,len(lines)):
            if len(lines[0]) != len(lines[i]):
                print ("[ERROR] all data file must have the same amount of data. Stop.")
                quit()
    
        xData = []
        yData = []
        linesList = []
        for e1 in lines:
            linesList.append([])
            for e2 in e1:
                linesList[len(linesList)-1].append(list(e2))
        #print ("linesList: ",linesList)
    
        for i in range(0,len(linesList[0]), 1):
            #print ("i = ",i)
            xData.append( int(linesList[0][i][0]) )
            l = []
            for j in range(len(linesList)):
                l.append( linesList[j][i][1] )
            yData.append(l)
            #print ( str(xData[-1]) + "," + str(yData[-1]))
    
        traceData(xData, yData, type="multi")