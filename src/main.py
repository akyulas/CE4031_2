from postgres_interface.postgres_wrapper import PostgresWrapper
from parser.find_difference import find_difference_between_two_query_plans
from parser.parser import Parser
import tkinter as tk
from PIL import ImageTk, Image
import networkx as nx
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import random


LARGE_FONT = ("Verdana",12)
HEIGHT = 500
WIDTH = 600
postgres_wrapper = PostgresWrapper()
newParser = Parser()
conn = None
G1 = None
G2 = None

def set_input(textbox, value):
    textbox.config(state='normal')
    textbox.delete('1.0', tk.END)
    textbox.insert(tk.END, value)
    textbox.config(state='disabled')

def submitLogin(host, dbname, user, password, port):
    try:
        port_no = int(port)
    except:
        port_no = None
    if not port_no:
        conn, connected = postgres_wrapper.connect_to_postgres_db(host, dbname, user, password)
    else:
        conn, connected = postgres_wrapper.connect_to_postgres_db(host, dbname, user, password, port_no)
    
def getQueryPlan(q1,q2,r1):
    old_query = q1
    new_query = q2

    result_1, success_1 = postgres_wrapper.get_query_plan_of_query(old_query)
    result_2, success_2 = postgres_wrapper.get_query_plan_of_query(new_query)

    newParser.update_graphs_with_new_query_plans(result_1, result_2)
    plan = newParser.get_difference_between_old_and_new_graphs(old_query, new_query)
    set_input(r1,plan)

def hierarchy_pos(G, root, levels=None, width=1., height=1.):
    '''If there is a cycle that is reachable from root, then this will see infinite recursion.
       G: the graph
       root: the root node
       levels: a dictionary
               key: level number (starting from 0)
               value: number of nodes in this level
       width: horizontal space allocated for drawing
       height: vertical space allocated for drawing'''
    TOTAL = "total"
    CURRENT = "current"
    def make_levels(levels, node=root, currentLevel=0, parent=None):
        """Compute the number of nodes for each level
        """
        if not currentLevel in levels:
            levels[currentLevel] = {TOTAL : 0, CURRENT : 0}
        levels[currentLevel][TOTAL] += 1
        neighbors = G.neighbors(node)
        for neighbor in neighbors:
            if not neighbor == parent:
                levels =  make_levels(levels, neighbor, currentLevel + 1, node)
        return levels

    def make_pos(pos, node=root, currentLevel=0, parent=None, vert_loc=0):
        dx = 1/levels[currentLevel][TOTAL]
        left = dx/2
        pos[node] = ((left + dx*levels[currentLevel][CURRENT])*width, vert_loc)
        levels[currentLevel][CURRENT] += 1
        neighbors = G.neighbors(node)
        for neighbor in neighbors:
            if not neighbor == parent:
                pos = make_pos(pos, neighbor, currentLevel + 1, node, vert_loc-vert_gap)
        return pos
    if levels is None:
        levels = make_levels({})
    else:
        levels = {l:{TOTAL: levels[l], CURRENT:0} for l in levels}
    vert_gap = height / (max([l for l in levels])+1)
    return make_pos({})
 
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
        if isinstance(frame, QPTPage):
            frame.refresh()
        frame.tkraise()



class HomePage(tk.Frame):
    title = 'Home Page'
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
        
        frame1_relx = 0.025 
        frame1_rely = 0.075
        frame1_relwidth = 0.95
        frame1_relheight = 0.95
        frame = tk.Frame(self,bg='#900C3F')
        frame.place(relx = frame1_relx, rely=frame1_rely, relwidth=frame1_relwidth, relheight=frame1_relheight)

        q1_relx = 0.025
        q1_rely = 0.25
        q_relwidth = 0.95
        q_relheight = 0.1

        hosttext = tk.Text(frame,font=40)
        hosttext.insert(tk.END,'Host')
        hosttext.place(relx = q1_relx,rely= q1_rely, relwidth=q_relwidth, relheight=q_relheight)

        q1_relx = 0.025
        q1_rely = 0.35
        q_relwidth = 0.95
        q_relheight = 0.1

        dbnametext = tk.Text(frame,font=40)
        dbnametext.insert(tk.END,'dbname')
        dbnametext.place(relx = q1_relx,rely= q1_rely, relwidth=q_relwidth, relheight=q_relheight)

        q1_relx = 0.025
        q1_rely = 0.45
        q_relwidth = 0.95
        q_relheight = 0.1

        usertext = tk.Text(frame,font=40)
        usertext.insert(tk.END,'user')
        usertext.place(relx = q1_relx,rely= q1_rely, relwidth=q_relwidth, relheight=q_relheight)

        q1_relx = 0.025
        q1_rely = 0.55
        q_relwidth = 0.95
        q_relheight = 0.1

        passwordtext = tk.Text(frame,font=40)
        passwordtext.insert(tk.END,'password')
        passwordtext.place(relx = q1_relx,rely= q1_rely, relwidth=q_relwidth, relheight=q_relheight)

        q1_relx = 0.025
        q1_rely = 0.65
        q_relwidth = 0.95
        q_relheight = 0.1

        porttext = tk.Text(frame,font=40)
        porttext.insert(tk.END,'port')
        porttext.place(relx = q1_relx,rely= q1_rely, relwidth=q_relwidth, relheight=q_relheight)

        submit = tk.Button(frame,text='Submit', command=lambda:submitLogin(hosttext.get("1.0","end-1c"),dbnametext.get("1.0","end-1c"),
                                                                           usertext.get("1.0","end-1c"), passwordtext.get("1.0","end-1c"), porttext.get("1.0","end-1c")))
        submit.place(relx=0.5, rely=0.8, relwidth = 0.08, relheight=0.08, anchor='center')





class QueryPage(HomePage):
    title = "Query Page"
    
    def __init__(self,parent,controller):
        HomePage.__init__(self,parent,controller)

        
        frame1_relx = 0.05 
        frame1_rely = 0.1
        frame1_relwidth = 0.40
        frame1_relheight = 0.85
        frame = tk.Frame(self,bg='#900C3F')
        frame.place(relx = frame1_relx, rely=frame1_rely, relwidth=frame1_relwidth, relheight=frame1_relheight)
        
        frame2_relx = 0.55
        frame2_rely = 0.1
        frame2_relwidth = 0.40
        frame2_relheight = 0.85
        frame2 = tk.Frame(self,bg='#900C3F')
        frame2.place(relx= frame2_relx,rely=frame2_rely, relwidth=frame2_relwidth, relheight=frame2_relheight)
        
        #query textbox
        q1_relx = 0.025
        q1_rely = 0.025
        q2_relx = 0.025
        q2_rely  = 0.525
        q_relwidth = 0.95
        q_relheight = 0.45
        
        textbox = tk.Text(frame,font=40)
        textbox.insert(tk.END,'Query 1')
        textbox.place(relx = q1_relx,rely= q1_rely, relwidth=q_relwidth, relheight=q_relheight)
        #
        textbox2 = tk.Text(frame, font=40)
        textbox2.insert(tk.END,'Query 2')
        textbox2.place(relx = q2_relx,rely=q2_rely, relwidth=q_relwidth, relheight=q_relheight)
        
        #query plan display box
        bg_color = 'white'
        r_relx = 0.025
        r_rely = 0.025
        r_relwidth = 0.95
        r_relheight = 0.95
        
        
        results = tk.Text(frame2)
        results.insert(tk.END,'Output')
        results.config(font=40, bg=bg_color, state='disabled')
        results.place(relx=r_relx,rely =r_rely,relwidth= r_relwidth, relheight=r_relheight)
        
        submit = tk.Button(self,text='Submit', command=lambda:getQueryPlan(textbox.get("1.0","end-1c"),textbox2.get("1.0","end-1c"),
                                                                           results))
        submit.place(relx=0.5, rely=0.5, relwidth = 0.08, relheight=0.08, anchor='center')
    
#Query PLan Tree Page
class QPTPage(HomePage):
    title = "Query Tree Page"
    def __init__(self,parent,controller):
        HomePage.__init__(self,parent,controller)
        
        #networkx graph1
        self.f1 = plt.figure(figsize=(5,5))
        self.a1 = self.f1.add_subplot(111)

        G1, G2 = newParser.get_graphs_for_visualizations()
        # G1 = nx.gnp_random_graph(20,0.5)
        nx.draw_networkx(G1,ax=self.a1)
        self.canvas1 = FigureCanvasTkAgg(self.f1,self)
        self.canvas1.get_tk_widget().pack(side='left', fill =tk.BOTH, expand = True)
        
        #networkx graph2
        self.f2 = plt.figure(figsize=(5,5))
        self.a2 = self.f2.add_subplot(111)
        # G2 = nx.gnp_random_graph(10,0.3)
        nx.draw_networkx(G2,ax=self.a2)
        self.canvas2 = FigureCanvasTkAgg(self.f2,self)
        self.canvas2.get_tk_widget().pack(side='left', fill =tk.BOTH, expand = True)
    
    def refresh(self):
        self.a1.clear()
        self.a2.clear()
        G1, G2 = newParser.get_graphs_for_visualizations()
        
        
        # G1 = nx.gnp_random_graph(20,0.5)
        pos_1 = hierarchy_pos(G1.reverse(),0)
        nx.draw(G1, ax=self.a1, pos=pos_1, with_labels=True)

        # nx.draw_planar(G1,ax=self.a1, with_labels= True)
        
        #networkx graph2
        # G2 = nx.gnp_random_graph(10,0.3)
        pos_2 = hierarchy_pos(G2.reverse(),0)
        nx.draw(G2, ax=self.a2, pos=pos_2, with_labels=True)
        # nx.draw_planar(G2,ax=self.a2, with_labels= True)

        self.canvas1.draw()
        self.canvas2.draw()

app = SeaofFrames()
app.minsize(width = WIDTH, height = HEIGHT)



app.mainloop()


