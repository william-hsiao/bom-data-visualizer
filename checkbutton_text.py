from tkinter import *
master = Tk()
var1 = IntVar()
Checkbutton(master, text="male", variable=var1, onvalue=1, offvalue=0).grid(row=0, sticky=W)
var2 = IntVar()
Checkbutton(master, text="female", variable=var2).grid(row=1, sticky=W)
print(var1)
mainloop()
