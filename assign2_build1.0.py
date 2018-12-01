
###################################################################
#
#   CSSE1001 - Assignment 2
#
#   Student Number: 43936973
#
#   Student Name: WEN-YUAN WILLIAM HSIAO
#
###################################################################

#####################################
# Support given below - DO NOT CHANGE
#####################################

from assign2_support import *

#####################################
# End of support 
#####################################

# Add your code here

class TemperatureData(object):
    """ A class for storing sets of temperature data within a dictionary
    """
    def __init__(self):
        """ Constructor: TemperatureData()"""
        self._stations = []
        self._data = {}
        self._status = []
        self._station_name = ''
                
    def load_data(self, filename):
        """ Loads in data from the given filename (of the form StationName.txt)

        load_data(str) -> None
        """
        
        self._load_station = Station(filename)
        self._station_name = self._load_station.get_name()
        self._stations.append(self._station_name)
        self._data[self._station_name] = self._load_station
        self._status.append(True)

    def get_data(self):
        """ Returns the dictionary of station data

        get_data() -> dict(str: Station)
        """
        return self._data

    def toggle_selected(self, i):
        """ Toggles the selected data value on/off

        toggle_selected(int) -> None        
        """
        self._status[i] = not self._status[i]
        
    def is_selected(self, i):
        """ Check if selected data is on

        is_selected(int) -> bool
        """
        return self._status[i] 

    def get_stations(self):
        """ Returns a list of station in the order loaded

        get_stations() -> List(str)
        """
        return self._stations

    def get_ranges(self):
        """ Returns the min and max of the year and temperature in the data

        get_ranges() -> (int, int, float, float)
        """
        min_year = 9999.9
        max_year = 0
        min_temp = 9999.9
        max_temp = 0

        for i in self._stations:
            _ymin, _ymax = self._data[i].get_year_range()
            _tmin, _tmax = self._data[i].get_temp_range()
            
            if _ymin < min_year:
                min_year = _ymin
            if _ymax > max_year:
                max_year = _ymax
            if _tmin < min_temp:
                min_temp = _tmin
            if _tmax > max_temp:
                max_temp = _tmax
             
        return (min_year, max_year, min_temp, max_temp)

    def get_station_name(self):

        return self._station_name





class Plotter(tk.Canvas):
    """ A 'widget' to plot data points """
    def __init__(self, canvas, data):
        self._data = data
        self._coords = None
        self._canvas = canvas
      
    def refresh(self):
        min_year, max_year, min_temp, max_temp = self._data.get_ranges()
        self._coords = CoordinateTranslator(self._canvas.winfo_width(), self._canvas.winfo_height(),\
                                            min_year, max_year, min_temp, max_temp)
        self._canvas.delete(tk.ALL)
        for station in self._data.get_stations():
            if self._data.is_selected(self._data.get_stations().index(station)):
                data_coords = []
                for entry in self._data.get_data()[station].get_data_points():
                    year = entry[0]
                    temp = entry[1]
                    coord = self._coords.temperature_coords(year, temp)
                    data_coords.append(coord)
                self._line = self._canvas.create_line(data_coords,\
                                                   fill=COLOURS[self._data.get_stations().index(station)])



class SelectionFrame(tk.Frame):
    """
    include label and Checkbutton for each loaded station (in the order loaded)

    """
    def __init__(self, master, plotter, dataframe, data):
        super().__init__(master)
        tk.Label(self, text="Station Selection: ").pack(side=tk.LEFT)
        self._stations = data.get_stations()
        self._plotter = plotter
        self._data = data
        self._status = {}
        self._dataframe = dataframe

    def add_entry(self, station_name):
        index = self._stations.index(station_name)
        self._status[station_name] = tk.IntVar()
        self._status[station_name].set(1)
        chckbtn = tk.Checkbutton(self, text=station_name, variable=self._status[station_name],\
                                 fg=COLOURS[index], command=lambda:self.toggle_selected(index))
        chckbtn.pack(side=tk.LEFT)
        self._dataframe.add_display(station_name, index)
        self._plotter.refresh()
        self._dataframe.update()
        self._dataframe.redraw_line()

    def toggle_selected(self, index):
        self._data.toggle_selected(index)
        self._plotter.refresh()
        self._dataframe.update()



        
class DataFrame(tk.Frame):
    def __init__(self, master, canvas, plotter, data):
        super().__init__(master)
        self._plotter = plotter
        self._canvas = canvas
        self._year = None
        self._data = data
        self._display = {}
        self._line = None
        self._first_press = False
        self._click_coord = None
        self._canvas_width = None

        self._data_lbl = tk.Label(self, text='     ')
        self._data_lbl.pack(side=tk.LEFT)

    def update(self):
        if self._first_press and self._data.get_data() != {}:
            self._data_lbl.config(text="Data for " + str(self._year) + ":       ")
            for station in self._data.get_stations():
                index = self._data.get_stations().index(station)
                if self._data.is_selected(index):
                    temp = self._data.get_data()[station].get_temp(self._year)
                    if temp != None:
                        self._display[station].config(text="{:<15}".format(temp)) 
                    else:
                        self._display[station].config(text="{:<15}".format(''))
                else:
                    self._display[station].config(text="{:<15}".format(''))
                
    def add_display(self, station, index):
        self._display[station] = tk.Label(self, text='     ', fg=COLOURS[index])
        self._display[station].pack(side=tk.LEFT)

    def press(self, e):
        if self._data.get_data() != {}:
            if self._first_press == False:
                self._first_press = True
            self._click_coord = e
            self._canvas_width = self._canvas.winfo_width()
            self._canvas.delete(self._line)
            min_year, max_year, min_temp, max_temp = self._data.get_ranges()
            self._xscale = (max_year - min_year)/self._canvas_width
            self._year = int(e.x * self._xscale +0.5) + min_year
            self._line = self._canvas.create_line([(e.x, 0), (e.x, self._canvas.winfo_height())])
            self.update()

    def redraw_line(self):
        if self._click_coord != None:
            min_year, max_year, min_temp, max_temp = self._data.get_ranges()
            self._xscale = self._canvas.winfo_width()/self._canvas_width
            self._x = self._click_coord.x * self._xscale
            self._line = self._canvas.create_line([(self._x, 0), (self._x, self._canvas.winfo_height())])
            
class TemperaturePlotApp(object):
    def __init__(self, master):
        self._data = TemperatureData()

        self._canvas = tk.Canvas(master, bg='white')
        self._plotter = Plotter(self._canvas, self._data)
        self._canvas.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self._dataframe = DataFrame(master, self._canvas, self._plotter, self._data)
        self._dataframe.pack(side=tk.TOP, expand=False, fill=tk.X)
        self._canvas.bind("<Button-1>", self._dataframe.press)
        self._canvas.bind("<B1-Motion>", self._dataframe.press)
        self._canvas.bind("<Configure>", self.resize)

        self._selectframe = SelectionFrame(master, self._plotter, self._dataframe, self._data)
        self._selectframe.pack(side=tk.TOP, expand=False, fill=tk.X)
        
        self._master = master
        master.title("Max Temperature Plotter")
        menubar = tk.Menu(master)
        master.config(menu=menubar)
        filemenu = tk.Menu(menubar)
        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Open", command=self.open_file)

    def resize(self, e):
        self._plotter.refresh()
        self._dataframe.redraw_line()
        
    def open_file(self):
        filename = filedialog.askopenfilename()
        try:
            self._data.load_data(filename)
            self._selectframe.add_entry(self._data.get_station_name())
        except:
            tk.messagebox.showerror('File Error', message=filename + ' is a invalid data file')

        

##################################################
# !!!!!! Do not change (or add to) the code below !!!!!
###################################################

def main():
    root = tk.Tk()
    app = TemperaturePlotApp(root)
    root.geometry("800x400")
    root.mainloop()

if __name__ == '__main__':
    main()
