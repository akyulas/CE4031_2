from postgres_interface.postgres_wrapper import PostgresWrapper
from qt_parser.main_parser import Parser
import tkinter as tk
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import random
import re


LARGE_FONT = ("Verdana",12)
HEIGHT = 500
WIDTH = 600
postgres_wrapper = PostgresWrapper()
newParser = Parser()
conn = None
G1 = None
G2 = None

def makeEntry(parent, caption, width=None, **options):
    tk.Label(parent, text=caption).pack(side="top")
    entry = tk.Entry(parent)
    if width:
        entry.config(width=width)
    entry.pack(side="top", **options)
    return entry


def set_input(textbox, value):
    textbox.config(state='normal')
    textbox.delete('1.0', tk.END)
    textbox.insert(tk.END, value)
    textbox.config(state='disabled')
	
def handleDBStatus(connected, db_status):
    if(connected):
        db_status.config(text = 'Database Connected',bg = 'green', font = ("Verdana",10))
    else:
        tk.messagebox.showerror("Error","Connection failed")
        db_status.config(text= "Database Disconnected", bg='red', font = ("Verdana",10))

def submitLogin(host, dbname, user, password, port, db_status):
    empty = False
    connected = False
    inputs = {'Database URL' : host, 'Database Name' : dbname, "User": user, "Password" : password}
    err_msg = ''
    for key,value in inputs.items():
        if len(value.strip()) == 0:
            empty = True
            err_msg += key + "\n"
    if(empty):
        tk.messagebox.showerror("Please fill", err_msg)

    else:
        try:
            port_no = int(port)
        except:
            port_no = None
        if not port_no:
            conn, connected = postgres_wrapper.connect_to_postgres_db(host, dbname, user, password)
            handleDBStatus(connected,db_status)
        else:
            conn, connected = postgres_wrapper.connect_to_postgres_db(host, dbname, user, password, port_no)
            handleDBStatus(connected,db_status)

 
def getQueryPlan(q1,q2,r1):
    old_query = q1
    new_query = q2

    old_query = re.sub("\s+" , " ", old_query)
    new_query = re.sub("\s+" , " ", new_query)

    result_1, success_1 = postgres_wrapper.get_query_plan_of_query(old_query)
    result_2, success_2 = postgres_wrapper.get_query_plan_of_query(new_query)

    if not success_2 and not success_1:
        newParser.update_graphs_with_new_query_plans(None, None)
        plan = "Both inputs are invalid. Please input valid SQL queries in the textbox."
        set_input(r1,plan)
    elif not success_2:
        newParser.update_graphs_with_new_query_plans(result_1, None)
        plan = "Invalid new query. Please input a valid SQL query."
        set_input(r1,plan)
    elif not success_1 :
        newParser.update_graphs_with_new_query_plans(None, result_2)
        plan = "Invalid old query. Please input a valid SQL query."
        set_input(r1, plan)
    else:
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
        frame.tkraise()
        if isinstance(frame, QPTPage):
            frame.refresh(frame.empty_label1, frame.empty_label2)
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
        
    
#Home Page
class HomePage(BasePage):
    title = 'Home Page'

    def __init__(self, parent, controller):
        BasePage.__init__(self, parent, controller)
        tk.Label(self, text= self.title, font = LARGE_FONT).pack(pady=10,padx=10)

        
        db_status = tk.Label(self, text= "Database Disconnected", bg='red', font = ("Verdana",10))
        db_status.pack(pady = 5, padx = 10)  

        entry_frame = tk.Frame(self, bd=1, relief="solid")
        entry_frame.place(relx = 0.2, rely =0.2, relwidth = 0.6, relheight=0.6)
        

        url = makeEntry(entry_frame, "Database URL:",padx = 10, pady=10,fill ='both')
       
        dbname = makeEntry(entry_frame, "Database Name:",padx = 10, pady=10,fill ='both')
        
        port = makeEntry(entry_frame, "Database Port (Port 5432 if empty):",padx = 10, pady=10,fill ='both')
        
        user = makeEntry(entry_frame, "User:",padx = 10, pady=10,fill ='both')      

        password = makeEntry(entry_frame, "Password:",padx = 10, pady=10,fill ='both')
       
        submit_button = tk.Button(entry_frame, text = "Submit",
        command = lambda:submitLogin(url.get(), dbname.get(), user.get(),password.get(), port.get(), db_status)).pack(side = 'bottom', pady=10,padx=10)
		
		
	
		


class QueryPage(BasePage):
    title = "Query Page"
    
    def __init__(self,parent,controller):
        BasePage.__init__(self,parent,controller)
        tk.Label(self, text= self.title, font = LARGE_FONT).pack(pady=10,padx=10)

        
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
class QPTPage(BasePage):
    title = "Query Tree Page"
    
    def __init__(self,parent,controller):
        BasePage.__init__(self,parent,controller)
        tk.Label(self, text= self.title, font = LARGE_FONT).pack(pady=10,padx=10)

        #networkx graph1
        self.f1 = plt.figure(figsize=(5,5))
        self.a1 = self.f1.add_subplot(111)
    
        G1, G2 = newParser.get_graphs_for_visualizations()

        nx.draw_networkx(G1,ax=self.a1)
        
        self.canvas1 = FigureCanvasTkAgg(self.f1,self)
        self.canvas1.get_tk_widget().pack(side='left', fill =tk.BOTH, expand = True)


        self.empty_label1 = tk.Label(self, text = "no query plan to show")
        # self.update_graph_from_query_plan(self.old_graph, query_plan_1)
        self.empty_label1.place(relx = 0.15, rely = 0.5, relwidth = 0.2, relheight=0.1)

       
        #networkx graph2
        self.f2 = plt.figure(figsize=(5,5))
        self.a2 = self.f2.add_subplot(111)
     

        # G2 = nx.gnp_random_graph(10,0.3)
        nx.draw_networkx(G2,ax=self.a2)
        self.canvas2 = FigureCanvasTkAgg(self.f2, self)
        self.canvas2.get_tk_widget().pack(side='left', fill =tk.BOTH, expand = True)

        self.empty_label2 = tk.Label(self, text = "no query plan to show")
        self.empty_label2.place(relx = 0.65, rely = 0.5, relwidth = 0.2, relheight=0.1)
    
    def refresh(self,empty_label1,empty_label2):
        self.a1.clear()
        self.a2.clear()
        self.a1.axis('off')
        self.a2.axis('off')
    

      
        G1, G2 = newParser.get_graphs_for_visualizations()
        

        if (len(G1.nodes()) !=0 ):
            empty_label1.place_forget()
            pos_1 = hierarchy_pos(G1.reverse(),0)
            nx.draw(G1, ax=self.a1, pos=pos_1, with_labels=True)
            self.canvas1.draw()
        else:
            self.canvas1.draw()
            empty_label1.place(relx = 0.15, rely = 0.5, relwidth = 0.2, relheight=0.1)

        if(len(G2.nodes()) !=0):
            empty_label2.place_forget()
            pos_2 = hierarchy_pos(G2.reverse(),0)
            nx.draw(G2, ax=self.a2, pos=pos_2, with_labels=True)
            self.canvas2.draw()

        else:
            self.canvas2.draw()
            empty_label2.place(relx = 0.65, rely = 0.5, relwidth = 0.2, relheight=0.1)


app = SeaofFrames()
app.minsize(width = WIDTH, height = HEIGHT)



app.mainloop()


