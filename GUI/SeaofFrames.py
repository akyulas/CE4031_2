import tkinter as tk
#from PIL import ImageTk, Image 
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt





LARGE_FONT = ("Verdana",12)
HEIGHT = 500
WIDTH = 600

def makeentry(parent, caption, width=None, **options):
    tk.Label(parent, text=caption).pack(side="top")
    entry = tk.Entry(parent)
    if width:
        entry.config(width=width)
    entry.pack(side="top", **options)
    return entry


class SeaofFrames(tk.Tk):
    def __init__(self,*args,**kwargs):
        tk.Tk.__init__(self,*args,**kwargs)
        container = tk.Frame(self,width=100, height=100, background="bisque")
        container.pack(side = "top", fill = "both", expand = True)
        container.grid_rowconfigure(0,weight=1)
        container.grid_columnconfigure(0,weight=1)
   
        self.frames = {}
        for F in (HomePage, QueryPage, QPTPage):
            frame = F(container,self)
            self.frames[F] = frame
            frame.grid(row = 0, column = 0,sticky ="nsew")
        
        self.show_frame(HomePage)
 
     
        
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        

class BasePage(tk.Frame): 
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        
        menu_frame = tk.Frame(self,  bg='#0082FF')
        menu_frame.pack()
        title_frame = tk.Frame(self,  bg='#FF2E00')
        title_frame.pack(side ='left')
        
     
        button = tk.Button(menu_frame, text = "Home Page",
                            command=lambda:controller.show_frame(HomePage))
        button.pack(side = 'left', pady=10,padx=10, fill ='both')
        
        button2 = tk.Button(menu_frame, text = "Query Page",
                            command=lambda:controller.show_frame(QueryPage),)
        button2.pack(side = 'left',pady=10,padx=10,fill='both')
        button3 = tk.Button(menu_frame, text = "Query Plan Tree",
                            command=lambda:controller.show_frame(QPTPage))
        button3.pack(side = 'left',pady=10,padx=10,fill='both')
        
        tk.Label(self, text= self.title, font = LARGE_FONT).pack(pady=10,padx=10)


#Home Page
class HomePage(BasePage):
    title = 'Home Page'
    


    def __init__(self, parent, controller):
        BasePage.__init__(self, parent, controller)
        
        entry_frame = tk.Frame(self, bd=1, relief="solid")
        entry_frame.place(relx = 0.2, rely =0.2, relwidth = 0.6, relheight=0.6)

        url = makeentry(entry_frame, "Database URL",padx = 10, pady=10, fill ='both')
        
        port = makeentry(entry_frame, "Database port",padx = 10, pady=10,fill ='both')
        
        name = makeentry(entry_frame, "Database name",padx = 10, pady=10,fill ='both')
        
        password = makeentry(entry_frame, "Database password",padx = 10, pady=10,fill ='both')
        
        submit_button = tk.Button(entry_frame, text = "Submit").pack(side = 'bottom', pady=10,padx=10)
        
        
        
        
#        db_url = tk.Entry(self,)

    
        
        
        



#Query Page
class QueryPage(BasePage):
    title = "Query Page"
    
    def __init__(self,parent,controller):
        BasePage.__init__(self,parent,controller)
        
        frame = tk.Frame(self,bg='#900C3F')
        frame.place(relx = 0.05, rely=0.1, relwidth=0.40, relheight=0.85)
        
        frame2 = tk.Frame(self,bg='#900C3F')
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
        
        
        submit = tk.Button(self,text='submit', command=lambda:getQueryPlan(textbox.get("1.0","end-1c"),textbox2.get("1.0","end-1c"),
                                                                           results,results2))
        submit.place(relx=0.5, rely=0.5, relwidth = 0.08, relheight=0.08, anchor='center')
        
        def set_input(textbox, value):
            textbox.config(state='normal')
            textbox.delete('1.0', tk.END)
            textbox.insert(tk.END, value)
            textbox.config(state='disabled')
            
        def getQueryPlan(q1,q2,r1,r2):
            plan1 = q1 + " paste postgres query 1 plan"
            plan2 = q2 + " paste postgres query 2 plan"
            set_input(r1,plan1)
            set_input(r2,plan2)
            #get query plan code
            


#Query PLan Tree Page
class QPTPage(BasePage):
    title = "Query Tree Page"
    def __init__(self,parent,controller):
        BasePage.__init__(self,parent,controller)
        
        #networkx graph1
        f1 = plt.figure(figsize=(5,5))
        a1 = f1.add_subplot(111)
        G1 = nx.gnp_random_graph(20,0.5)
        nx.draw_networkx(G1,ax=a1)
        canvas1 = FigureCanvasTkAgg(f1,self)
        canvas1.get_tk_widget().pack(side='left', fill =tk.BOTH, expand = True)
        
        #networkx graph2
        f2 = plt.figure(figsize=(5,5))
        a2 = f2.add_subplot(111)
        G2 = nx.gnp_random_graph(10,0.3)
        nx.draw_networkx(G2,ax=a2)
        canvas2 = FigureCanvasTkAgg(f2,self)
        canvas2.get_tk_widget().pack(side='left', fill =tk.BOTH, expand = True)
       
      
        
       
       
   
       


app = SeaofFrames()
app.minsize(width = WIDTH, height = HEIGHT)



app.mainloop()