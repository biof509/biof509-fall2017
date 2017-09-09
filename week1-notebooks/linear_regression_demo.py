import numpy as np
import pandas as pd

from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, TextInput
from bokeh.plotting import figure, output_notebook, show
from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox, gridplot, column

x = pd.DataFrame({'a': np.random.random(50) * 10,
                    'b': np.random.normal(10, 3, size=50),
                    'c': np.random.normal(5, 1, size=50)})
y = 5 * x['a'] + 6 * x['b'] + 11 * x['c'] + np.random.normal(0, 5, size=50)

a_source = ColumnDataSource(data=dict(x=[], y=[]))

# Set up plot
a_plot = figure(plot_height=300, plot_width=300, title="Variable A",
              tools="crosshair,pan,reset,save,wheel_zoom",)

a_plot.line('x', 'y', source=a_source)
a_plot.circle(x['a'], y)



b_source = ColumnDataSource(data=dict(x=[], y=[]))

# Set up plot
b_plot = figure(plot_height=300, plot_width=300, title="Variable B",
              tools="crosshair,pan,reset,save,wheel_zoom",)

b_plot.line('x', 'y', source=b_source)
b_plot.circle(x['b'], y)


c_source = ColumnDataSource(data=dict(x=[], y=[]))

# Set up plot
c_plot = figure(plot_height=300, plot_width=300, title="Variable C",
              tools="crosshair,pan,reset,save,wheel_zoom",)

c_plot.line('x', 'y', source=c_source)
c_plot.circle(x['c'], y)


pred_plot = figure(plot_height=300, plot_width=300, title="Prediction vs Actual",
              tools="crosshair,pan,reset,save,wheel_zoom",)

pred_source = ColumnDataSource(data=dict(x=[], y=[]))
pred_plot.circle('x', 'y', source=pred_source)



resid_plot = figure(plot_height=300, plot_width=300, title="Residuals",
              tools="crosshair,pan,reset,save,wheel_zoom",)
resid_source = ColumnDataSource(data=dict(x=[], y=[]))
resid_plot.circle('x', 'y', source=resid_source)



a_inter = Slider(title="A Intercept", value=0, start=-10, end=200, step=1)
a_grad = Slider(title="A Gradient", value=0, start=-10, end=30, step=1)
b_inter = Slider(title="B Intercept", value=0, start=-10, end=200, step=1)
b_grad = Slider(title="B Gradient", value=0, start=-10, end=30, step=1)
c_inter = Slider(title="C Intercept", value=0, start=-10, end=200, step=1)
c_grad = Slider(title="C Gradient", value=0, start=-10, end=30, step=1)

store = [{'min':x['a'].min(), 'max':x['a'].max(), 'inter':a_inter, 'grad':a_grad, 'source':a_source},
        {'min':x['b'].min(), 'max':x['b'].max(), 'inter':b_inter, 'grad':b_grad, 'source':b_source},
        {'min':x['c'].min(), 'max':x['c'].max(), 'inter':c_inter, 'grad':c_grad, 'source':c_source}]

def update_data(attrname, old, new):
    for s in store:
        v_x = np.linspace(s['min'], s['max'], 10)
        v_y = s['grad'].value * v_x + s['inter'].value
        #print(v_x.shape, v_y.shape)
        s['source'].data = dict(x=v_x, y=v_y)
    
    p_x = a_grad.value * x['a'] + b_grad.value * x['b'] + c_grad.value * x['c']
    p_x += a_inter.value + b_inter.value + c_inter.value
    #print(y.shape, p_x.shape)
    pred_source.data = dict(x=p_x, y=y)
    resid_source.data = dict(x=y, y=p_x - y)

update_data('','','')

for w in [a_inter, a_grad, b_inter, b_grad, c_inter, c_grad]:
    w.on_change('value', update_data)


# Set up layouts and add to document
inputs = widgetbox(a_inter, a_grad, b_inter, b_grad, c_inter, c_grad)
curdoc().add_root(column(row(a_plot, b_plot, c_plot, inputs),
                            row(pred_plot, resid_plot)))