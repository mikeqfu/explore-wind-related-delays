""" Utilities - Helper functions """

import copy
import inspect
import json
import os
import pickle
import re
import string
import subprocess

import Levenshtein
import fuzzywuzzy.process
import matplotlib.cm
import matplotlib.colors
import matplotlib.pyplot
import numpy as np
import pandas as pd


# Type to confirm whether to proceed or not
def confirmed(prompt=None, resp=False):
    """
    Reference: http://code.activestate.com/recipes/541096-prompt-the-user-for-confirmation/

    :param prompt:
    :param resp:
    :return:

    Example: confirm(prompt="Create Directory?", resp=True)
             Create Directory? Yes|No:

    """
    if prompt is None:
        prompt = "Confirmed? "

    if resp is True:  # meaning that default response is True
        prompt = "{} [{}]|{}: ".format(prompt, "Yes", "No")
    else:
        prompt = "{} [{}]|{}: ".format(prompt, "No", "Yes")

    ans = input(prompt)
    if not ans:
        return resp

    if re.match('[Yy](es)?', ans):
        return True
    if re.match('[Nn](o)?', ans):
        return False


# ====================================================================================================================
""" Change directories """


# Change directory
def cd(*directories):
    # Current working directory
    path = os.getcwd()
    for directory in directories:
        path = os.path.join(path, directory)
    return path


# Change directory to "Data"
def cdd(*directories):
    path = cd("Data")
    for directory in directories:
        path = os.path.join(path, directory)
    return path


# Change directory to "RailwayCode"
def cdd_rc(*directories):
    path = cdd("Network", "Railway Codes")
    for directory in directories:
        path = os.path.join(path, directory)
    return path


# ====================================================================================================================
""" Save and Load files """


# Save pickles
def save_pickle(pickle_data, path_to_pickle):
    """
    :param pickle_data: any object that could be dumped by the 'pickle' package
    :param path_to_pickle: [str] local file path
    :return: whether the data has been successfully saved
    """
    pickle_filename = os.path.basename(path_to_pickle)
    print("{} \"{}\" ... ".format("Updating" if os.path.isfile(path_to_pickle) else "Saving", pickle_filename), end="")
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path_to_pickle)), exist_ok=True)
        pickle_out = open(path_to_pickle, 'wb')
        pickle.dump(pickle_data, pickle_out)
        pickle_out.close()
        print("Successfully.")
    except Exception as e:
        print("Failed. {}.".format(e))


# Load pickles
def load_pickle(path_to_pickle, verbose=False):
    """
    :param path_to_pickle: [str] local file path
    :param verbose: [bool] Whether to print note
    :return: the object retrieved from the pickle
    """
    print("Loading \"{}\" ... ".format(os.path.basename(path_to_pickle)), end="") if verbose else None
    try:
        pickle_in = open(path_to_pickle, 'rb')
        pickle_data = pickle.load(pickle_in)
        pickle_in.close()
        print("Successfully.") if verbose else None
    except Exception as e:
        print("Failed. {}.".format(e)) if verbose else None
        pickle_data = None
    return pickle_data


# Save json file
def save_json(json_data, path_to_json):
    """
    :param json_data: any object that could be dumped by the 'json' package
    :param path_to_json: [str] local file path
    :return: whether the data has been successfully saved
    """
    json_filename = os.path.basename(path_to_json)
    print("{} \"{}\" ... ".format("Updating" if os.path.isfile(path_to_json) else "Saving", json_filename), end="")
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path_to_json)), exist_ok=True)
        json_out = open(path_to_json, 'w')
        json.dump(json_data, json_out)
        json_out.close()
        print("Successfully.")
    except Exception as e:
        print("Failed. {}.".format(e))


# Load json file
def load_json(path_to_json, verbose=False):
    """
    :param path_to_json: [str] local file path
    :param verbose: [bool] Whether to print note
    :return: the json data retrieved
    """
    print("Loading \"{}\" ... ".format(os.path.basename(path_to_json)), end="") if verbose else None
    try:
        json_in = open(path_to_json, 'r')
        json_data = json.load(json_in)
        json_in.close()
        print("Successfully.") if verbose else None
    except Exception as e:
        print("Failed. {}.".format(e)) if verbose else None
        json_data = None
    return json_data


# Save Excel workbook
def save_excel(excel_data, path_to_excel, sep, index, sheet_name, engine='xlsxwriter'):
    """
    :param excel_data: any [DataFrame] that could be dumped saved as a Excel workbook, e.g. '.csv', '.xlsx'
    :param path_to_excel: [str] local file path
    :param sep: [str] separator for saving excel_data to a '.csv' file
    :param index: [bool]
    :param sheet_name: [str] name of worksheet for saving the excel_data to a e.g. '.xlsx' file
    :param engine: [str] ExcelWriter engine; pandas writes Excel files using the 'xlwt' module for '.xls' files and the
                        'openpyxl' or 'xlsxWriter' modules for '.xlsx' files.
    :return: whether the data has been successfully saved or updated
    """
    excel_filename = os.path.basename(path_to_excel)
    _, save_as = os.path.splitext(excel_filename)
    print("{} \"{}\" ... ".format("Updating" if os.path.isfile(path_to_excel) else "Saving", excel_filename), end="")
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path_to_excel)), exist_ok=True)
        if excel_filename.endswith(".csv"):  # Save the data to a .csv file
            excel_data.to_csv(path_to_excel, index=index, sep=sep, na_rep='', float_format=None, columns=None,
                              header=True, index_label=None, mode='w', encoding=None, compression='infer',
                              quoting=None, quotechar='"', line_terminator=None, chunksize=None,
                              tupleize_cols=None, date_format=None, doublequote=True, escapechar=None,
                              decimal='.')
        else:  # Save the data to a .xlsx or .xls file, e.g. excel_filename.endswith(".xlsx")
            xlsx_writer = pd.ExcelWriter(path_to_excel, engine)
            excel_data.to_excel(xlsx_writer, sheet_name, index=index, na_rep='', float_format=None,
                                columns=None, header=True, index_label=None, startrow=0, startcol=0,
                                engine=None, merge_cells=True, encoding=None, inf_rep='inf', verbose=True,
                                freeze_panes=None)
            xlsx_writer.save()
            xlsx_writer.close()
        print("Successfully.")
    except Exception as e:
        print("Failed. {}.".format(e))


# Save data locally (.pickle, .csv or .xlsx)
def save(data, path_to_file, sep=',', index=False, sheet_name='Sheet1', engine='xlsxwriter', deep_copy=True):
    """
    :param data: any object that could be dumped
    :param path_to_file: [str] local file path
    :param sep: [str] separator for '.csv'
    :param index:
    :param engine: [str] 'xlwt' for .xls; 'xlsxwriter' or 'openpyxl' for .xlsx
    :param sheet_name: [str] name of worksheet
    :param deep_copy: [bool] whether make a deep copy of the data before saving it
    :return: whether the data has been successfully saved or updated
    """
    # Make a copy the original data
    dat = copy.deepcopy(data) if deep_copy else copy.copy(data)

    # The specified path exists?
    os.makedirs(os.path.dirname(os.path.abspath(path_to_file)), exist_ok=True)

    if isinstance(dat, pd.DataFrame) and dat.index.nlevels > 1:
        dat.reset_index(inplace=True)

    # Save the data according to the file extension
    if path_to_file.endswith((".csv", ".xlsx", ".xls")):
        save_excel(dat, path_to_file, sep, index, sheet_name, engine)
    elif path_to_file.endswith(".json"):
        save_json(dat, path_to_file)
    else:
        save_pickle(dat, path_to_file)
        if not path_to_file.endswith(".pickle"):
            print("Note that the file extension is not among the recognisable formats of this 'save()' function.")


# Save a figure using plt.savefig()
def save_fig(path_to_fig_file, dpi):
    fig_filename = os.path.basename(path_to_fig_file)
    print("{} \"{}\" ... ".format("Updating" if os.path.isfile(path_to_fig_file) else "Saving", fig_filename), end="")
    try:
        matplotlib.pyplot.savefig(path_to_fig_file, dpi=dpi)
        _, save_as = os.path.splitext(path_to_fig_file)
        if save_as == ".svg":
            path_to_emf = path_to_fig_file.replace(save_as, ".emf")
            subprocess.call(["C:\\Program Files\\Inkscape\\inkscape.exe", '-z', path_to_fig_file, '-M', path_to_emf])
        print("Successfully.")
    except Exception as e:
        print("Failed. {}.".format(e))


# ====================================================================================================================
""" Misc """


# Check if a str expresses a float
def is_float(text):
    try:
        float(text)
        return True
    except ValueError:
        try:
            float(re.sub('[()~]', '', text))
            return True
        except ValueError:
            return False


# Reset double indexes
def reset_double_indexes(data):
    levels = list(data.columns)
    column_names = []
    for i in range(len(levels)):
        col_name = levels[i][0] + '_' + levels[i][1]
        column_names += [col_name]
    data.columns = column_names
    data.reset_index(inplace=True)
    return data


# Find from a list the closest, case-insensitive, string to the given one
def find_match(x, lookup):
    if x is '' or x is None:
        return None
    else:
        for y in lookup:
            if re.match(x, y, re.IGNORECASE):
                return y


#
def find_closest_text(x, lookup):
    ratios = [Levenshtein.ratio(x, y) for y in lookup]
    return lookup[np.argmax(ratios)]


#
def find_nearest(vector, target):
    my_array = np.array(vector)
    diff = my_array - target
    mask = np.ma.less_equal(diff, 0)
    # We need to mask the negative differences and zero since we are looking for values above
    if all(mask):
        return None
    else:
        # returns None if target is greater than any value
        masked_diff = np.ma.masked_array(diff, mask)
        return masked_diff.argmin()


# Check whether a string contains digits
def contains_digits(text):
    x = re.compile('\\d').search(text)
    return bool(x)


# Find the closest date of the given 'data' from a list of dates
def find_closest_date(dates_list, date):
    return min(dates_list, key=lambda x: abs(x - date))


# Calculate the n-th percentile
def percentile(n):
    def np_percentile(x):
        return np.percentile(x, n)

    np_percentile.__name__ = 'percentile_%s' % n
    return np_percentile


# Calculate interquartile range
def interquartile_range(x):
    """
    Alternative way: using scipy.stats.iqr(x)
    """
    return np.subtract(*np.percentile(x, [75, 25]))


# Get the given variable's name
def get_variable_names(*var):
    local_variables = inspect.currentframe().f_back.f_locals.items()
    variable_list = []
    for v in var:
        var_str = [var_name for var_name, var_val in local_variables if var_val is v]
        if len(var_str) > 1:
            var_str = [x for x in var_str if '_' not in x][0]
        else:
            var_str = var_str[0]
        variable_list.append(var_str)
    return variable_list


# A function for working with colour ramps
def cmap_discretisation(cmap_param, no_of_colours):
    """
    :param cmap_param: colormap instance, e.g. cm.jet
    :param no_of_colours: number of colours
    :return: a discrete colormap from the continuous colormap cmap.

    Reference: http://sensitivecities.com/so-youd-like-to-make-a-map-using-python-EN.html#.WbpP0T6GNQB

    Example:
        x = np.resize(np.arange(100), (5, 100))
        d_jet = cmap_discretize(cm.jet, 5)
        plt.imshow(x, cmap=d_jet)

    """
    if isinstance(cmap_param, str):
        cmap_param = matplotlib.cm.get_cmap(cmap_param)
    colors_i = np.concatenate((np.linspace(0, 1., no_of_colours), (0., 0., 0., 0.)))
    colors_rgba = cmap_param(colors_i)
    indices = np.linspace(0, 1., no_of_colours + 1)
    c_dict = {}
    for ki, key in enumerate(('red', 'green', 'blue')):
        c_dict[key] = [(indices[x], colors_rgba[x - 1, ki], colors_rgba[x, ki]) for x in range(no_of_colours + 1)]
    return matplotlib.colors.LinearSegmentedColormap(cmap_param.name + '_%d' % no_of_colours, c_dict, 1024)


# A function for working with colour color bars
def colour_bar_index(no_of_colours, cmap_param, labels=None, **kwargs):
    """
    :param no_of_colours: number of colors
    :param cmap_param: colormap instance, eg. cm.jet
    :param labels:
    :param kwargs:
    :return:

    Reference: http://sensitivecities.com/so-youd-like-to-make-a-map-using-python-EN.html#.WbpP0T6GNQB

    This is a convenience function to stop making off-by-one errors
    Takes a standard colour ramp, and discretizes it, then draws a colour bar with correctly aligned labels

    """
    cmap_param = cmap_discretisation(cmap_param, no_of_colours)
    mappable = matplotlib.cm.ScalarMappable(cmap=cmap_param)
    mappable.set_array(np.array([]))
    mappable.set_clim(-0.5, no_of_colours + 0.5)
    color_bar = matplotlib.pyplot.colorbar(mappable, **kwargs)
    color_bar.set_ticks(np.linspace(0, no_of_colours, no_of_colours))
    color_bar.set_ticklabels(range(no_of_colours))
    if labels:
        color_bar.set_ticklabels(labels)
    return color_bar


# Get upper and lower bounds for removing extreme outliers
def get_bounds_extreme_outliers(data_set, k=1.5):
    q1, q3 = np.percentile(data_set, 25), np.percentile(data_set, 75)
    iqr = q3 - q1
    lower_bound = np.max([0, q1 - k * iqr])
    upper_bound = q3 + k * iqr
    return lower_bound, upper_bound


# Convert compressed sparse matrix to dictionary
def csr_matrix_to_dict(csr_matrix, vectorizer):
    features = vectorizer.get_feature_names()
    dict_data = []
    for i in range(len(csr_matrix.indptr) - 1):
        sid, eid = csr_matrix.indptr[i: i + 2]
        row_feat = [features[x] for x in csr_matrix.indices[sid:eid]]
        row_data = csr_matrix.data[sid:eid]
        dict_data.append(dict(zip(row_feat, row_data)))

    return pd.Series(dict_data).to_frame('word_count')


# Split a dataframe by initial letter (in the alphabetic order) of a string column
def split_dataframe_by_initials(dataframe, by_column_name):
    dataframe[by_column_name].fillna('', inplace=True)
    dataframe['temp'] = dataframe[by_column_name].map(lambda x: x[0].capitalize() if len(x) > 0 else x)

    data_slices = []
    for initial in string.ascii_uppercase:
        data_slice = dataframe[dataframe.temp == initial]
        data_slice.drop('temp', axis=1, inplace=True)
        data_slices.append(data_slice)

    dataframe.drop('temp', axis=1, inplace=True)
    keys = ['_'.join([by_column_name, initial]) for initial in list(string.ascii_uppercase)]

    return dict(zip(keys, data_slices))


# Form a file name in terms of specific 'Route' and 'weather' category
def make_filename(base_name, route, weather, *extra_suffixes, save_as=".pickle"):
    if route is not None:
        route_lookup = load_json(cdd("Network\\Routes", "route-names.json"))
        route = find_match(route, route_lookup['Route'])
    if weather is not None:
        weather_category_lookup = load_json(cdd("Weather", "weather-categories.json"))
        weather = find_match(weather, weather_category_lookup['WeatherCategory'])
    filename_suffix = [s for s in (route, weather) if s is not None]  # "s" stands for "suffix"
    filename = "-".join([base_name] + filename_suffix + [str(s) for s in extra_suffixes]) + save_as
    return filename


# Subset the required data given 'route' and 'weather'
def subset(data, route=None, weather_category=None, reset_index=False):
    if data is None:
        data_subset = None
    else:
        route_lookup = list(set(data.Route))
        weather_category_lookup = list(set(data.WeatherCategory))
        # Select data for a specific route and weather category
        if not route and not weather_category:
            data_subset = data.copy()
        elif route and not weather_category:
            data_subset = data[data.Route == fuzzywuzzy.process.extractOne(route, route_lookup, score_cutoff=10)[0]]
        elif not route and weather_category:
            data_subset = data[
                data.WeatherCategory ==
                fuzzywuzzy.process.extractOne(weather_category, weather_category_lookup, score_cutoff=10)[0]]
        else:
            data_subset = data[
                (data.Route == fuzzywuzzy.process.extractOne(route, route_lookup, score_cutoff=10)[0]) &
                (data.WeatherCategory ==
                 fuzzywuzzy.process.extractOne(weather_category, weather_category_lookup, score_cutoff=10)[0])]
        # Reset index
        if reset_index:
            data_subset.reset_index(inplace=True)  # dat.index = range(len(dat))
    return data_subset


# Get Angle of Line between Two Points
def get_angle_of_line_between(p1, p2, in_degrees=False):
    x_diff = p2.x - p1.x
    y_diff = p2.y - p1.y
    angle = np.arctan2(y_diff, x_diff)  # in radians
    if in_degrees:
        angle = np.degrees(angle)
    return angle
