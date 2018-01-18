import numpy as np
import pandas as pd
import logging
from bokeh.io import curdoc
from bokeh.layouts import row, column, layout
from bokeh.models import ColumnDataSource, Title
from bokeh.models.widgets import PreText, Select
from bokeh.plotting import figure
from bokeh.io import output_file, show
from bokeh.layouts import widgetbox
from bokeh.models.widgets import CheckboxGroup, CheckboxButtonGroup, Select
from bokeh.palettes import Spectral11
import time
import redis
import json
from functools import partial
from collections import defaultdict
import pmt_data
import static.divs as static_divs
from bokeh.io import output_file, show, curdoc
from bokeh.models import ColumnDataSource, HoverTool, Range1d
from bokeh.plotting import figure
from bokeh.layouts import row, column, layout, gridplot
from bokeh.models.widgets import PreText, Div
#from bokeh.sampledata.periodic_table import elements
from bokeh.layouts import widgetbox
from bokeh.transform import dodge, factor_cmap
import random
import numpy as np
#from collections import Counter
import pandas as pd
from bokeh.palettes import Spectral4
import pmt_data
#from collections import Counter, OrderedDict
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
MAXDATA = 100
NROWS = 2
NCOLS = 2
UPDATE = 300 #ms
XSIZE = 35
YSIZE = 15
TITLE = 'PMT HV Status'
props = {}
dsource = ColumnDataSource()
plots = []
doc = curdoc()
def build_layout():
    head = Div(text=static_divs.header, width=800, height=300)
    top = widgetbox(head)
    xrange = [0.5, max(dsource.data['column'])+.5]
    yrange = [max(dsource.data['row'])+.5, 0.5]
    p = figure(plot_width=XSIZE*(len(dsource.data['column'])+1), plot_height=YSIZE*(len(dsource.data['row'])+1), title=TITLE,
           x_range=xrange, y_range=yrange, toolbar_location=None, tools="")
    plots.append(p)
    p.rect('column', 'row', 0.9, 0.9, source=dsource,color='grey', fill_alpha=0.5,)
    text_props = {"source": dsource, "text_align": "left", "text_baseline": "middle"}
    def x(dx):
        return dodge('column',dx, range=p.x_range )
    def y(dy):
        return dodge('row', dy, range=p.y_range )
    r1 = p.text(x=x(-0.41), y=y(0), text='voltage', text_color='vcolor', **text_props)
    r1.glyph.text_font_size = '8pt'
    r1 = p.text(x=x(-0.4), y=y(0.2), text='current', text_color='icolor', **text_props)
    r1.glyph.text_font_size = '8pt'
    r1 = p.text(x=x(-0.4), y=y(-0.3), text='channel',text_color='ccolor', **text_props)
    r1.glyph.text_font_style="bold"
    # r1 = p.circle(x=x(-0.35), y=y(-0.3), line_color='ccolor',alpha=0.2, source=dsource)
    # r1.glyph.fill_color= 'blue'
    # r1.glyph.line_width = 3
    # r1.glyph.size = 25
    r1 = p.text(x=x(-0.2), y=y(-0.3), text='status',text_color='scolor', **text_props)
    #r1 = p.text(x=x(-0.2), y=y(-0.3), text=['status'], **text_props)
    r1.glyph.text_font_style="bold"
    r1.glyph.text_font_size = '10pt'
    names = list(dsource.data.keys())

    ttips = [(name.title(),'@{}'.format(name)) for name in names]
    p.add_tools(HoverTool(tooltips = ttips))

    p.toolbar.logo = None
    p.toolbar_location = None
    p.xaxis.major_tick_line_color = None  # turn off x-axis major ticks
    p.xaxis.minor_tick_line_color = None  # turn off x-axis minor ticks
    p.yaxis.major_tick_line_color = None  # turn off y-axis major ticks
    p.yaxis.minor_tick_line_color = None  # turn off y-axis minor ticks
    p.xaxis.major_tick_line_color = None  # turn off y-axis minor ticks
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.xaxis.major_label_text_font_size = '0pt'  # preferred method for removing tick labels
    p.yaxis.major_label_text_font_size = '0pt'  # preferred method for removing tick labels
    p.axis.major_label_standoff = 0
    p.outline_line_width = 7
    p.outline_line_alpha = 0.3
    #p.legend.orientation = "horizontal"
    #p.legend.location ="top_center"
    lo = column(top,p)
    return lo

def formatter(x):
    if isinstance(x, float):
        return round(x,3)
    else:
        return x

def pmt_update():
    dsource.data = pmt_data.dstore['latest_values']

def status_update():
    for p in plots:
        if pmt_data.dstore['live']:
            p.outline_line_color = "green"
            p.title = Title(text='PMT HV Status: Online')
        else:
            p.outline_line_color = "red"
            p.title = Title(text='PMT HV Status: Offline',
                            background_fill_alpha=0.4,
                             background_fill_color='red')
    #log.info(str(dsource.data))
for _ in range(20):
    if len(pmt_data.dstore['latest_values']):
        pmt_update()
        lo = build_layout()
        break
    else:
        log.info('waiting for data...')
        time.sleep(0.1)
else:
    raise Exception('Failed to load data.')
doc.add_root(lo)
doc.title = "Monitor"
doc.add_periodic_callback(pmt_update, UPDATE)
doc.add_periodic_callback(status_update, UPDATE/2)
