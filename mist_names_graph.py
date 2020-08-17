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
from bokeh.io import output_file, show
from bokeh.models import (BoxZoomTool,HoverTool,WheelZoomTool,PanTool,
                          Plot, Range1d, ResetTool, TapTool, EdgesAndLinkedNodes,
                          NodesAndLinkedEdges)
from bokeh.palettes import Spectral8
from bokeh.models.graphs import from_networkx
from bokeh.embed import file_html
from bokeh.resources import CDN
import pandas as pd


# Run the bokeh app using this in command-line: bokeh serve mist_names_graph.py

class Node:
    def __init__(self, pid, edges, closeness):
        # Turns out this is unnecessary-- unless things become a bit more complex down the road.
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
            while (df.columns[col] != 'Study1id'):
                if not np.isnan(row[col]):
                    C.append(int(row[col]))
                col += 1
            pid = int(row[0])
            self.Nodes[pid] = Node(pid, L, C)
    def get_Edges_and_Nodes(self, biDirection=False):
        edges = []
        edgesSeen = set()
        uniqN = set()
        for pid in self.Nodes:
            for friendid in self.Nodes[pid].edges:
                newEdge = [pid, friendid]
                if biDirection:
                    tupEdge = tuple(sorted(newEdge))
                    if tupEdge in edgesSeen:
                        continue
                edges.append(newEdge)
                uniqN.add(pid)
                uniqN.add(friendid)
                if biDirection:
                    edgesSeen.add(tupEdge)
        return edges, uniqN
    def CreateGraph(self, retG=False):
        G = nx.DiGraph()
        edges, uN = self.get_Edges_and_Nodes()
        G.add_edges_from(edges)
        for pid in self.Nodes:
            if pid not in uN:
                G.add_node(pid)
        if retG:
            return G
        properties = nx.spring_layout(G)
        return properties
    def get_Nodes_inSpace(self, prop):
        x, y, friends, avgcloseness, index = [], [], [], [], []
        for pid in prop:
            x.append(prop[pid][0])
            y.append(prop[pid][1])
            index.append(pid)
            if pid in G.Nodes:
                friends.append(self.Nodes[pid].friends)
                avgcloseness.append(self.Nodes[pid].avgcloseness)
            else:
                friends.append(0)
                avgcloseness.append(0)
        return {'x':x, 'y':y, 'friends':friends, 'avgCloseness':avgcloseness, 'index':index}
    def get_Edges_inSpace(self, prop):
        xs, ys, xe, ye = [], [], [], []
        for pid in self.Nodes:
            for friendid in self.Nodes[pid].edges:
                xs.append(prop[pid][0])
                ys.append(prop[pid][1])
                xe.append(prop[friendid][0])
                ye.append(prop[friendid][1])
        return {'xs':xs, 'ys':ys, 'xe':xe, 'ye':ye}
    
G = Graph()
G.linkNodes('Names_id_friends.csv')
prop = G.CreateGraph()
source = ColumnDataSource(data = G.get_Nodes_inSpace(prop))
arrowSource = ColumnDataSource(G.get_Edges_inSpace(prop))

hovertool = HoverTool(tooltips=[('index','@index'), ('friends', '@friends'), ('avgCloseness', '@avgCloseness')])
f1 = figure(tools=[hovertool, WheelZoomTool(), ResetTool(), PanTool(), TapTool()], plot_width=1000,plot_height=900,
        title="NY MIST Network Graph")

#f1.add_tools(hovertool, WheelZoomTool(), ResetTool(), PanTool())
# f1.add_layout(Arrow(end=VeeHead(size=15), x_start='xs', y_start='ys', x_end='xe', y_end='ye', source=arrowSource, line_alpha=0.4))
nodes = f1.circle('x', 'y', alpha=0.7, source=source, line_color=None, size=20, visible=False)

Gnx = G.CreateGraph(True)
friendsD = {source.data['index'][i]: source.data['friends'][i] for i in range(len(source.data['index']))}
avgCloseD = {source.data['index'][i]: source.data['avgCloseness'][i] for i in range(len(source.data['index']))}
nx.set_node_attributes(Gnx, friendsD, 'friends')
nx.set_node_attributes(Gnx, avgCloseD, 'avgCloseness')
graph_renderer = from_networkx(Gnx, nx.spring_layout, scale=1, center=(0,0))

graph_renderer.node_renderer.glyph = Circle(size=20, fill_alpha=0.7, fill_color=Spectral8[0])
graph_renderer.node_renderer.selection_glyph = Circle(size=20, fill_color=Spectral8[5])
graph_renderer.node_renderer.hover_glyph = Circle(size=20, fill_alpha=0.7, fill_color=Spectral8[1])

graph_renderer.edge_renderer.glyph = MultiLine(line_alpha=0.4, line_width=0.5)
graph_renderer.edge_renderer.selection_glyph = MultiLine(line_color=Spectral8[5], line_width=5)
graph_renderer.edge_renderer.hover_glyph = MultiLine(line_color=Spectral8[1], line_width=4)

graph_renderer.selection_policy = NodesAndLinkedEdges()
#graph_renderer.selection_policy = EdgesAndLinkedNodes()
graph_renderer.inspection_policy = NodesAndLinkedEdges()

f1.renderers.append(graph_renderer)

p = ROW([f1])
curdoc().add_root(p)

html = file_html(f1, CDN, "NY MIST Network Graph")
html_file = open("default.html", "w")
html_file.write(html)
html_file.close()

#p = ROW([COLUMN([tabs, left, Parms]), Middle, blanktext]+rowcols)

#curdoc().add_root(p)