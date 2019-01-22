# scripts to plot mean activity +/- sem

import pandas as pd
import matplotlib.pyplot as plt
import actiPy.preprocessing as prep
from actiPy.plots import multiple_plot_kwarg_decorator, set_title_decorator

@set_title_decorator
@multiple_plot_kwarg_decorator
def plot_means(data, **kwargs):
    
    """
    Function to plot the mean wave form from a split df
    :param grouped:
    :param kwargs:
    :return:
    """
    
    # find the conditions
    vals = data.index.get_level_values(0).unique()
    no_conditions = len(vals)

    # plot each condition on a separate subplot
    fig, ax = plt.subplots(nrows=no_conditions,
                           sharey=True,
                           sharex=True)
    for val, axis in zip(vals, ax):
        df = data.loc[val]
        mean = df.mean(axis=1)
        sem = df.sem(axis=1)

        axis.plot(mean)
        axis.fill_between(df.index, mean-sem, mean+sem, alpha=0.5)
        
        axis.set_ylabel(val)

    fig.subplots_adjust(hspace=0)
    
    params_dict = {
        "timeaxis": True,
        "interval": 6,
        "title": "Mean activity for each condition",
        "ylabel": "Mean activity +/- sem",
        "xlabel": "Circadian Time",
        "xlim": [df.index[0], (df.index[0] + pd.Timedelta('24H'))]
    }
    
    return fig, axis, params_dict

def plot_wave_from_df(data,
                      level: int=0,
                      **kwargs):
    """
    Takes input, groupsby values of level and passes split df to plot_means
    :param data:
    :param level:
    :return:
    """

    grouped = data.groupby(level=level).apply(prep.split_all_animals, **kwargs)
    
    grouped_cols = grouped.groupby(axis=1, level=level).mean()
    
    plot_means(grouped_cols, **kwargs)
