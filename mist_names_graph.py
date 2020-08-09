# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 14:28:25 2020

@author: Shakeel Farooq
"""

import networkx as nx
import numpy as np
from bokeh.layouts import row as ROW, column as COLUMN
from bokeh.models import ColumnDataSource
from bokeh.models import Button, Circle, MultiLine
from bokeh.models import RadioButtonGroup, Slider, Select, RangeSlider, Tabs
from bokeh.models import Panel, TextInput, PreText, Toggle
from bokeh.models import DataTable, TableColumn, CheckboxButtonGroup
from bokeh.models import Arrow, VeeHead
from bokeh.events import DoubleTap, MouseMove, Tap, MouseLeave
from bokeh.plotting import figure,curdoc
from bokeh.colors import RGB
import pandas as pd


# Run the bokeh app using this in command-line: bokeh serve mist_names_graph.py

class Node:
    def __init__(self, pid, edges, closeness):
        self.pid = pid
        self.edges = edges
        self.closeness = closeness
        self.friends = max([len(edges), len(closeness)])
        self.avgcloseness = np.mean(closeness) if len(closeness) > 0 else 'No Closeness Identified'

class Graph:
    def __init__(self):
        self.Nodes = {}
    def linkNodes(self, csvFile):
        df = pd.read_csv(csvFile)
        for index, row in df.iterrows():
            L, C = [], []
            col = 1
            while (df.columns[col] != 'Friend1Closeness'):
                if not np.isnan(row[col]):
                    L.append(int(row[col]))
                col += 1
            col = np.arange(len(df.columns))[df.columns=='Friend1Closeness'][0]
            while (df.columns[col] != 'Study1Name'):
                if not np.isnan(row[col]):
                    C.append(int(row[col]))
                col += 1
            pid = int(row[0])
            self.Nodes[pid] = Node(pid, L, C)
    def get_Edges(self):
        edges = []
        for pid in self.Nodes:
            for friendid in self.Nodes[pid].edges:
                edges.append([pid, friendid])
        return edges
    def CreateGraph(self):
        G = nx.DiGraph()
        G.add_edges_from(self.get_Edges())
        nx.draw_spring(G)
        return G
    
G = Graph()
G.linkNodes('FINAL DEIDENTIFIED FOR NY T1 STUDY 2.csv')

TOOLS = "box_select,poly_select,pan,wheel_zoom,help"
f1 = figure(tools=TOOLS,plot_width=1800,plot_height=800,
        title="Test Figure",
        active_drag='box_select')


p = ROW([f1])
curdoc().add_root(p)

#p = ROW([COLUMN([tabs, left, Parms]), Middle, blanktext]+rowcols)

#curdoc().add_root(p)