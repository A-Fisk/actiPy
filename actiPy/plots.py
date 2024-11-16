import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
idx = pd.IndexSlice

# Script for defining decorators to be used for plotting functions
# all plotting functions need to take fig, ax as *args, and return
# fig and ax and params dict


def draw_sighlines(yval: float,
                   sig_list: list,
                   label_loc_dict: dict,
                   minus_val: float,
                   plus_val: float,
                   curr_ax,
                   **kwargs):
    """
    Draws an hline at the position indicated in the sig list of indexes by
    looking it up in label_loc_dict then drawing a hline at the yval from
    loc mins_val to loc plus_val on curr_ax
    :param yval:
    :param sig_list:
    :param label_loc_dict:
    :param minus_val:
    :param plus_val:
    :param curr_ax:
    :return:
    """
    for xval in sig_list:
        curr_xval = label_loc_dict[xval]
        hxvals = [curr_xval - minus_val, curr_xval + plus_val]
        hxval_axes = curr_ax.transLimits.transform([(hxvals[0], 0),
                                                    (hxvals[1], 0)])
        hxval_axes_val = hxval_axes[:, 0]
        curr_ax.axhline(yval,
                        xmin=hxval_axes_val[0],
                        xmax=hxval_axes_val[1],
                        **kwargs)


def get_xval_dates(curr_xval,
                   minus_val: pd.Timedelta,
                   plus_val: pd.Timedelta,
                   curr_ax):
    """
    Works to get xvals to plot if dates
    :type plus_val: object
    :param sig_list:
    :param minus_val:
    :param plus_val:
    :param curr_ax:
    :return:
    """
    hxvals = [curr_xval - minus_val, curr_xval + plus_val]
    hxvals_num = [mdates.date2num(x) for x in hxvals]
    hxvals_transformed = curr_ax.transLimits.transform(
        [(hxvals_num[0], 0),
         (hxvals_num[1], 0)]
    )
    hxvals_trans_xvals = hxvals_transformed[:, 0]

    return hxvals_trans_xvals


def get_xtick_dict(curr_ax):
    """
    Returns a dict of the locations of where each label is
    Can then be used to find where to draw liens
    :param curr_ax:
    :return:
    """
    labels = curr_ax.get_xticklabels()
    locs = curr_ax.get_xticks()
    label_text = [x.get_text() for x in labels]
    label_loc_dict = dict(zip(label_text, locs))
    return label_loc_dict


def sig_locs_get(df: pd.DataFrame,
                 sig_col: str = "p-tukey",
                 sig_val: float = 0.05,
                 index_level2val: int = 0,
                 index_levelget: int = 0,
                 test_efsize: bool = True,
                 test_col: str = "efsize",
                 test_val: float = np.inf):
    """
    Finds where the sig_col is less than the sig_val for the index_level2val
    Used for a posthoc tukeys df as example where 0 =baseline-disrupted
    1=baseline-recovery etc.
    :param df:
    :param sig_col:
    :param sig_val:
    :param index_level2val:
    :return:
    """
    sig_mask = df[sig_col] < sig_val
    sig_vals = df[sig_mask]
    if test_efsize:
        test_mask = ~sig_vals['efsize'].isin([test_val, -test_val])
        sig_vals = sig_vals[test_mask]
    sig_index = sig_vals.loc[idx[:, index_level2val], :
                             ].index.get_level_values(index_levelget)

    return sig_index


def sig_line_coord_get(curr_ax,
                       sig_line_ylevel: float = 0.9):
    """
    Finds the sig_line_level in axes co-ordinates
    :param curr_ax:
    :param sig_line_ylevel:
    :return:
    """
    axes_to_data = curr_ax.transLimits.inverted()
    ycoords = (0.5, sig_line_ylevel)
    ycoords_data = axes_to_data.transform(ycoords)
    ycoord_data_val = ycoords_data[1]

    return ycoord_data_val
