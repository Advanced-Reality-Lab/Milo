from tkinter import *
import json
from tkinter.filedialog import asksaveasfile

ws = Tk()
ws.geometry('640x300')
ws.title('Python Guides')

test = 1


def jSONfile(path, fileName, data):
    json.dump(data, path)


path = './'


def check():
    x = int(ID.get())
    y = test * Name.get()
    z = Batch.get()
    print(x)
    print(y)
    print(z)
    data = {}
    data['ID'] = x
    data['Name'] = y
    data['Batch'] = z
    File = [('JSON_File', '*.json')]
    File_Name = 'service/config/conf.json'
    File_position = asksaveasfile(filetypes=File, defaultextension=json, initialfile='IOTEDU')
    jSONfile(File_position, File_Name, data)


id = Label(ws, text="ID:")
ID = Entry(ws)
name = Label(ws, text="Name:")
Name = Entry(ws)
batch = Label(ws, text="Batch:")
Batch = Entry(ws)

id.grid(row=0, column=0)
ID.grid(row=0, column=1)
name.grid(row=4, column=0)
Name.grid(row=4, column=1)
batch.grid(row=6, column=0)
Batch.grid(row=6, column=1)

submit = Button(ws, text='Submit', command=check).grid(row=8, column=1)

ws.mainloop()