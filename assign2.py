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
        """ Constructor: TemperatureData(dict(str: Station))"""
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
        """ Returns the station name of the loaded station

        get_station_name() -> str
        """

        return self._station_name





class Plotter(tk.Canvas):
    """ A 'widget' to plot data points """
    def __init__(self, parent):
        """ Widget to set the canvas to display selected data

        Constructor: Plotter(parent)
        """
        self._parent = parent
        self._data = self._parent._data
        self._coords = None
        self._canvas = self._parent._canvas

    def refresh(self):
        """ Updates the display

        refresh() -> None
        """
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
    """ A class to manage which data sets to display
    """
    def __init__(self, master, parent):
        """ Widget to set up frame to select loaded data to display

        Constructor: SelectionFrame(master, parent)
        """
        super().__init__(master)
        tk.Label(self, text="Station Selection: ").pack(side=tk.LEFT)
        self._parent = parent
        self._plotter = self._parent._plotter
        self._data = self._parent._data
        self._dataframe = self._parent._dataframe
        self._stations = self._data.get_stations()
        self._status = {}

    def add_entry(self, station):
        """ Adds a entry to the selection frame enabling toggle on/off of display

        add_entry(str) -> None
        """
        index = self._stations.index(station)
        self._status[station] = tk.IntVar()
        self._status[station].set(1)
        chckbtn = tk.Checkbutton(self, text=station, variable=self._status[station],\
                                 fg=COLOURS[index], command=lambda:self.toggle_selected(index))
        chckbtn.pack(side=tk.LEFT)
        self._dataframe.add_display(station, index)
        self._plotter.refresh()
        self._dataframe.update()
        self._dataframe.redraw_line()

    def toggle_selected(self, index):
        """ Turns on/off the inputted data on the display

        toggle_selected(int) -> None
        """
        self._data.toggle_selected(index)
        self._plotter.refresh()
        self._dataframe.update()
        self._dataframe.redraw_line()




class DataFrame(tk.Frame):
    """ Widget class to manage frame to display temperature of selected year
    """
    def __init__(self, master, parent):
        """Sets up frame to display temperature of selected year

        Constructor: DataFrame(master, parent)
        """
        super().__init__(master)
        self._parent = parent
        self._plotter = self._parent._plotter
        self._canvas = self._parent._canvas
        self._data = self._parent._data
        self._display = {}
        self._year = None
        self._line = None
        self._first_press = False
        self._click_coord = None
        self._canvas_width = None

        self._data_lbl = tk.Label(self, text='     ')
        self._data_lbl.pack(side=tk.LEFT)

    def update(self):
        """ Updates the temperatures displayed

        update() -> None
        """
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
        """ Adds a display for the inputted station

        add_display(str, int) -> None
        """
        self._display[station] = tk.Label(self, text='     ', fg=COLOURS[index])
        self._display[station].pack(side=tk.LEFT)

    def press(self, e):
        """ Draws a vertical line at the click coordinate

        press(Event) -> None
        """
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
        """ Redraws the line to the new scale

        redraw_line() -> None
        """
        if self._click_coord != None:
            min_year, max_year, min_temp, max_temp = self._data.get_ranges()
            self._xscale = self._canvas.winfo_width()/self._canvas_width
            self._x = self._click_coord.x * self._xscale
            self._line = self._canvas.create_line([(self._x, 0), (self._x, self._canvas.winfo_height())])




class TemperaturePlotApp(object):
    """Master class to manage the app components"""
    def __init__(self, master):
        """Initializes the app components

        Constructor: TemperaturePlotApp(master)
        """
        self._data = TemperatureData()

        self._canvas = tk.Canvas(master, bg='white')
        self._plotter = Plotter(self)
        self._canvas.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self._dataframe = DataFrame(master, self)
        self._dataframe.pack(side=tk.TOP, expand=False, fill=tk.X)
        self._canvas.bind("<Button-1>", self._dataframe.press)
        self._canvas.bind("<B1-Motion>", self._dataframe.press)
        self._canvas.bind("<Configure>", self.resize)

        self._selectframe = SelectionFrame(master, self)
        self._selectframe.pack(side=tk.TOP, expand=False, fill=tk.X)

        self._master = master
        master.title("Max Temperature Plotter")
        menubar = tk.Menu(master)
        master.config(menu=menubar)
        filemenu = tk.Menu(menubar)
        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Open", command=self.open_file)

    def resize(self, e):
        """ Updates display to new scale

        resize(Event) -> None
        """
        self._plotter.refresh()
        self._dataframe.redraw_line()

    def open_file(self):
        """ Opens file for data import

        open_file() -> None
        """
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
