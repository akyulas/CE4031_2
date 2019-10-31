import tkinter as tk
from PIL import ImageTk, Image


app = tk.Tk()

HEIGHT = 500
WIDTH = 600



def set_input(textbox, value):
    textbox.config(state='normal')
    textbox.delete('1.0', tk.END)
    textbox.insert(tk.END, value)
    textbox.config(state='disabled')

def getQueryPlan(q1,q2):
    plan = q1 + "paste postgres query plan"
    plan2 = q2 + "paste postgres query plan"
    set_input(results,plan)
    set_input(results2,plan2)
    #get query plan code
    

C = tk.Canvas(app, height=HEIGHT, width=WIDTH)
background_image=ImageTk.PhotoImage(file='background.png')
background_label = tk.Label(app, image=background_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)
C.pack()

frame = tk.Frame(app,  bg='#900C3F')
frame.place(relx = 0.05, rely=0.1, relwidth=0.40, relheight=0.85)

frame2 = tk.Frame(app,  bg='#900C3F')
frame2.place(relx= 0.55,rely=0.1, relwidth=0.40, relheight=0.85)

#query textbox
q_relx = 0.025
q_rely = 0.025
q_relwidth = 0.95
q_relheight = 0.45

textbox = tk.Text(frame,font=40)
textbox.insert(tk.END,'Query 1')
textbox.place(relx = q_relx,rely= q_rely, relwidth=q_relwidth, relheight=q_relheight)
#
textbox2 = tk.Text(frame2, font=40)
textbox2.insert(tk.END,'Query 2')
textbox2.place(relx = q_relx,rely=q_rely, relwidth=q_relwidth, relheight=q_relheight)

#query plan display box
bg_color = 'white'
r_relx = 0.025
r_rely = 0.525
r_relwidth = 0.95
r_relheight = 0.45


results = tk.Text(frame)
results.insert(tk.END,'Query Plan 1')
results.config(font=40, bg=bg_color, state='disabled')
results.place(relx=r_relx,rely =r_rely,relwidth= r_relwidth, relheight=r_relheight)

results2 = tk.Text(frame2)
results2.insert(tk.END,'Query Plan 2')
results2.config(font=40, bg=bg_color, state = 'disabled')
results2.place(relx=r_relx,rely =r_rely,relwidth= r_relwidth, relheight=r_relheight)


submit = tk.Button(app, text='submit')
submit = tk.Button(app, text='submit', command=lambda: getQueryPlan(textbox.get("1.0","end-1c"),textbox2.get("1.0","end-1c")))
submit.place(relx=0.5, rely=0.5, relwidth = 0.08, relheight=0.08, anchor='center')








app.mainloop()