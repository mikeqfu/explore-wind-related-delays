""" Read and clean data of NR_VEG database """

import datetime
import os
import re

import pandas as pd

import converters
import database_utils as db
from utils import save, save_pickle, load_pickle, find_match, reset_double_indexes

# ====================================================================================================================
""" Change directories """


# Change directory to "Data\\Vegetation\\Database\\Tables"
def cdd_veg_db_tables(*directories):
    path = db.cdd_veg_db("Tables")
    os.makedirs(path, exist_ok=True)
    for directory in directories:
        path = os.path.join(path, directory)
    return path


# Change directory to "Data\\Vegetation\\Database\\Views"
def cdd_veg_db_views(*directories):
    path = db.cdd_veg_db("Views")
    os.makedirs(path, exist_ok=True)
    for directory in directories:
        path = os.path.join(path, directory)
    return path


# Route names dictionary
def get_route_names_dict(reverse=False):
    # title_case = sorted(get_furlong_location()['Route'].unique().tolist())
    title_cases = [
        'Anglia', 'East Midlands', 'Kent', 'LNE', 'LNW North', 'LNW South', 'Scotland', 'Sussex', 'Wales', 'Wessex',
        'Western Thames Valley', 'Western West']
    # upper_case = sorted(get_du_route()['Route'].unique().tolist())
    upper_cases = [
        'ANGLIA', 'EAST MIDLANDS', 'KENT', 'LNE', 'LNW North', 'LNW South', 'SCOTLAND', 'SUSSEX', 'WALES', 'WESSEX',
        'WESTERN Thames Valley', 'WESTERN West']
    if not reverse:
        route_names_dict = dict(zip(title_cases, upper_cases))
    else:
        route_names_dict = dict(zip(upper_cases, title_cases))
    return route_names_dict


# ====================================================================================================================
""" Get table data from the NR_VEG database """


# Get primary keys of a table in database 'NR_VEG'
def veg_pk(table_name):
    pri_key = db.get_pri_keys(db_name='NR_VEG', table_name=table_name)
    return pri_key


# Get AdverseWind
def get_adverse_wind(update=False):
    table_name = 'AdverseWind'
    path_to_file = cdd_veg_db_tables(table_name + ".pickle")

    if os.path.isfile(path_to_file) and not update:
        adverse_wind = load_pickle(path_to_file)
    else:
        try:
            adverse_wind = db.read_veg_table(table_name, index_col=veg_pk(table_name), save_as=".csv")
            save_pickle(adverse_wind, path_to_file)
        except Exception as e:
            print(e)
            print("Getting '{}' ... Failed.".format(table_name))
            adverse_wind = None

    return adverse_wind


# Get CuttingAngleClass
def get_cutting_angle_class(update=False):
    table_name = 'CuttingAngleClass'
    path_to_file = cdd_veg_db_tables(table_name + ".pickle")

    if os.path.isfile(path_to_file) and not update:
        cutting_angle = load_pickle(path_to_file)
    else:
        try:
            cutting_angle = db.read_veg_table(table_name, index_col=veg_pk(table_name), save_as=".csv")
            save_pickle(cutting_angle, path_to_file)
        except Exception as e:
            print(e)
            print("Getting '{}' ... Failed.".format(table_name))
            cutting_angle = None

    return cutting_angle


# Get CuttingDepthClass
def get_cutting_depth_class(update=False):
    table_name = 'CuttingDepthClass'
    path_to_file = cdd_veg_db_tables(table_name + ".pickle")

    if os.path.isfile(path_to_file) and not update:
        cutting_depth = load_pickle(path_to_file)
    else:
        try:
            cutting_depth = db.read_veg_table(table_name, index_col=veg_pk(table_name), save_as=".csv")
            save_pickle(cutting_depth, path_to_file)
        except Exception as e:
            print(e)
            print("Getting '{}' ... Failed.".format(table_name))
            cutting_depth = None

    return cutting_depth


# Get DUList
def get_du_list(index=True, update=False):
    table_name = 'DUList'
    path_to_file = cdd_veg_db_tables(table_name + ".pickle")

    if os.path.isfile(path_to_file) and not update:
        du_list = load_pickle(path_to_file)
    else:
        try:
            du_list = db.read_veg_table(table_name, index_col=veg_pk(table_name), save_as=".csv")
            save_pickle(du_list, path_to_file)
            if not index:
                du_list = du_list.reset_index()
        except Exception as e:
            print(e)
            print("Getting '{}' ... Failed.".format(table_name))
            du_list = None

    return du_list


# Get PathRoute
def get_path_route(update=False):
    table_name = 'PathRoute'
    path_to_file = cdd_veg_db_tables(table_name + ".pickle")

    if os.path.isfile(path_to_file) and not update:
        path_route = load_pickle(path_to_file)
    else:
        try:
            path_route = db.read_veg_table(table_name, index_col=veg_pk(table_name), save_as=".csv")
            save_pickle(path_route, path_to_file)
        except Exception as e:
            print(e)
            print("Getting '{}' ... Failed.".format(table_name))
            path_route = None

    return path_route


# Get Routes
def get_du_route(update=False):
    table_name = 'Routes'
    path_to_file = cdd_veg_db_tables(table_name + ".pickle")

    if os.path.isfile(path_to_file) and not update:
        routes = load_pickle(path_to_file)
    else:
        try:
            # (Note that 'Routes' table contains information about Delivery Units)
            routes = db.read_veg_table(table_name, index_col=veg_pk(table_name), save_as=".csv")
            # Replace values in (index) column 'DUName'
            routes.index = routes.index.to_series().replace(
                {'Lanc&Cumbria MDU - HR1': 'Lancashire & Cumbria MDU - HR1',
                 'S/wel& Dud MDU - HS7': 'Sandwell & Dudley MDU - HS7'})
            # Replace values in column 'DUNameGIS'
            routes.DUNameGIS.replace({'IMDM  Lanc&Cumbria': 'IMDM Lancashire & Cumbria'}, inplace=True)
            save_pickle(routes, path_to_file)
        except Exception as e:
            print(e)
            print("Getting '{}' ... Failed.".format(table_name))
            routes = None

    return routes


# Get S8Data
def get_s8data_from_db_veg(update=False):
    table_name = 'S8Data'
    path_to_file = cdd_veg_db_tables(table_name + ".pickle")

    if os.path.isfile(path_to_file) and not update:
        s8data = load_pickle(path_to_file)
    else:
        try:
            s8data = db.read_veg_table(table_name, index_col=veg_pk(table_name), save_as=".csv")
            save_pickle(s8data, path_to_file)
        except Exception as e:
            print(e)
            print("Getting '{}' ... Failed.".format(table_name))
            s8data = None

    return s8data


# Get TreeAgeClass
def get_tree_age_class(update=False):
    table_name = 'TreeAgeClass'
    path_to_file = cdd_veg_db_tables(table_name + ".pickle")

    if os.path.isfile(path_to_file) and not update:
        tree_age_class = load_pickle(path_to_file)
    else:
        try:
            tree_age_class = db.read_veg_table(table_name, index_col=veg_pk(table_name), save_as=".csv")
            save_pickle(tree_age_class, path_to_file)
        except Exception as e:
            print(e)
            print("Getting '{}' ... Failed.".format(table_name))
            tree_age_class = None

    return tree_age_class


# Get TreeSizeClass
def get_tree_size_class(update=False):
    table_name = 'TreeSizeClass'
    path_to_file = cdd_veg_db_tables(table_name + ".pickle")

    if os.path.isfile(path_to_file) and not update:
        tree_size_class = load_pickle(path_to_file)
    else:
        try:
            tree_size_class = db.read_veg_table(table_name, index_col=veg_pk(table_name), save_as=".csv")
            save_pickle(tree_size_class, path_to_file)
        except Exception as e:
            print(e)
            print("Getting '{}' ... Failed.".format(table_name))
            tree_size_class = None

    return tree_size_class


# Get TreeType
def get_tree_type(update=False):
    table_name = 'TreeType'
    path_to_file = cdd_veg_db_tables(table_name + ".pickle")

    if os.path.isfile(path_to_file) and not update:
        tree_type = load_pickle(path_to_file)
    else:
        try:
            tree_type = db.read_veg_table(table_name, index_col=veg_pk(table_name), save_as=".csv")
            save_pickle(tree_type, path_to_file)
        except Exception as e:
            print(e)
            print("Getting '{}' ... Failed.".format(table_name))
            tree_type = None

    return tree_type


# Get FellingType
def get_felling_type(update=False):
    table_name = 'FellingType'
    path_to_file = cdd_veg_db_tables(table_name + ".pickle")

    if os.path.isfile(path_to_file) and not update:
        felling_type = load_pickle(path_to_file)
    else:
        try:
            felling_type = db.read_veg_table(table_name, index_col=veg_pk(table_name), save_as=".csv")
            save_pickle(felling_type, path_to_file)
        except Exception as e:
            print(e)
            print("Getting '{}' ... Failed.".format(table_name))
            felling_type = None

    return felling_type


# Get AreaWorkType
def get_area_work_type(update=False):
    table_name = 'AreaWorkType'
    path_to_file = cdd_veg_db_tables(table_name + ".pickle")

    if os.path.isfile(path_to_file) and not update:
        area_work_type = load_pickle(path_to_file)
    else:
        try:
            area_work_type = db.read_veg_table(table_name, index_col=veg_pk('AreaWorkType'), save_as=".csv")
            save_pickle(area_work_type, path_to_file)
        except Exception as e:
            print(e)
            print("Getting '{}' ... Failed.".format(table_name))
            area_work_type = None

    return area_work_type


# Get ServiceDetail
def get_service_detail(update=False):
    table_name = 'ServiceDetail'
    path_to_file = cdd_veg_db_tables(table_name + ".pickle")

    if os.path.isfile(path_to_file) and not update:
        service_detail = load_pickle(path_to_file)
    else:
        try:
            service_detail = db.read_veg_table(table_name, index_col=veg_pk('ServiceDetail'), save_as=".csv")
            save_pickle(service_detail, path_to_file)
        except Exception as e:
            print(e)
            print("Getting '{}' ... Failed.".format(table_name))
            service_detail = None

    return service_detail


# Get ServicePath
def get_service_path(update=False):
    table_name = 'ServicePath'
    path_to_file = cdd_veg_db_tables(table_name + ".pickle")

    if os.path.isfile(path_to_file) and not update:
        service_path = load_pickle(path_to_file)
    else:
        try:
            service_path = db.read_veg_table(table_name, index_col=veg_pk(table_name), save_as=".csv")
            save_pickle(service_path, path_to_file)
        except Exception as e:
            print(e)
            print("Getting '{}' ... Failed.".format(table_name))
            service_path = None

    return service_path


# Get Supplier
def get_supplier(update=False):
    table_name = 'Supplier'
    path_to_file = cdd_veg_db_tables(table_name + ".pickle")

    if os.path.isfile(path_to_file) and not update:
        supplier = load_pickle(path_to_file)
    else:
        try:
            supplier = db.read_veg_table(table_name, index_col=veg_pk(table_name), save_as=".csv")
            save_pickle(supplier, path_to_file)
        except Exception as e:
            print(e)
            print("Getting '{}' ... Failed.".format(table_name))
            supplier = None

    return supplier


# Get SupplierCosts
def get_supplier_costs(update=False):
    table_name = 'SupplierCosts'
    path_to_file = cdd_veg_db_tables(table_name + ".pickle")

    if os.path.isfile(path_to_file) and not update:
        supplier_costs = load_pickle(path_to_file)
    else:
        try:
            supplier_costs = db.read_veg_table(table_name, index_col=veg_pk(table_name), save_as=".csv")
            save_pickle(supplier_costs, path_to_file)
        except Exception as e:
            print(e)
            print("Getting '{}' ... Failed.".format(table_name))
            supplier_costs = None

    return supplier_costs


# Get SupplierCostsArea
def get_supplier_costs_area(update=False):
    table_name = 'SupplierCostsArea'
    path_to_file = cdd_veg_db_tables(table_name + ".pickle")

    if os.path.isfile(path_to_file) and not update:
        costs_area = load_pickle(path_to_file)
    else:
        try:
            costs_area = db.read_veg_table(table_name, index_col=veg_pk(table_name), save_as=".csv")
            save_pickle(costs_area, path_to_file)
        except Exception as e:
            print(e)
            print("Getting '{}' ... Failed.".format(table_name))
            costs_area = None

    return costs_area


# Get SupplierCostsSimple
def get_supplier_cost_simple(update=False):
    table_name = 'SupplierCostsSimple'
    path_to_file = cdd_veg_db_tables(table_name + ".pickle")

    if os.path.isfile(path_to_file) and not update:
        costs_simple = load_pickle(path_to_file)
    else:
        try:
            costs_simple = db.read_veg_table(table_name, index_col=veg_pk(table_name), save_as=".csv")
            save_pickle(costs_simple, path_to_file)
        except Exception as e:
            print(e)
            print("Getting '{}' ... Failed.".format(table_name))
            costs_simple = None

    return costs_simple


# Get TreeActionFractions
def get_tree_action_fractions(update=False):
    table_name = 'TreeActionFractions'
    path_to_file = cdd_veg_db_tables(table_name + ".pickle")

    if os.path.isfile(path_to_file) and not update:
        tree_action_fractions = load_pickle(path_to_file)
    else:
        try:
            tree_action_fractions = db.read_veg_table(table_name, index_col=veg_pk(table_name), save_as=".csv")
            save_pickle(tree_action_fractions, path_to_file)
        except Exception as e:
            print(e)
            print("Getting '{}' ... Failed.".format(table_name))
            tree_action_fractions = None

    return tree_action_fractions


# Get VegSurvTypeClass
def get_veg_surv_type_class(update=False):
    table_name = 'VegSurvTypeClass'
    path_to_file = cdd_veg_db_tables(table_name + ".pickle")

    if os.path.isfile(path_to_file) and not update:
        veg_surv_type_class = load_pickle(path_to_file)
    else:
        try:
            veg_surv_type_class = db.read_veg_table(table_name, index_col=veg_pk(table_name), save_as=".csv")
            save_pickle(veg_surv_type_class, path_to_file)
        except Exception as e:
            print(e)
            print("Getting '{}' ... Failed.".format(table_name))
            veg_surv_type_class = None

    return veg_surv_type_class


# Get WBFactors
def get_wb_factors(update=False):
    table_name = 'WBFactors'
    path_to_file = cdd_veg_db_tables(table_name + ".pickle")

    if os.path.isfile(path_to_file) and not update:
        wb_factors = load_pickle(path_to_file)
    else:
        try:
            wb_factors = db.read_veg_table(table_name, index_col=veg_pk(table_name), save_as=".csv")
            save_pickle(wb_factors, path_to_file)
        except Exception as e:
            print(e)
            print("Getting '{}' ... Failed.".format(table_name))
            wb_factors = None

    return wb_factors


# Get Weedspray
def get_weed_spray(update=False):
    table_name = 'Weedspray'
    path_to_file = cdd_veg_db_tables(table_name + ".pickle")

    if os.path.isfile(path_to_file) and not update:
        weed_spray = load_pickle(path_to_file)
    else:
        try:
            weed_spray = db.read_veg_table(table_name, index_col=veg_pk(table_name), save_as=".csv")
            save_pickle(weed_spray, path_to_file)
        except Exception as e:
            print(e)
            print("Getting '{}' ... Failed.".format(table_name))
            weed_spray = None

    return weed_spray


# Get WorkHours
def get_work_hours(update=False):
    table_name = 'WorkHours'
    path_to_file = cdd_veg_db_tables(table_name + ".pickle")

    if os.path.isfile(path_to_file) and not update:
        work_hours = load_pickle(path_to_file)
    else:
        try:
            work_hours = db.read_veg_table(table_name, index_col=veg_pk(table_name), save_as=".csv")
            save_pickle(work_hours, path_to_file)
        except Exception as e:
            print(e)
            print("Getting '{}' ... Failed.".format(table_name))
            work_hours = None

    return work_hours


# Get FurlongData
def get_furlong_data(set_index=False, pseudo_amendment=True, update=False):
    """
    Equipment Class: VL ('VEGETATION - 1/8 MILE SECTION')
    1/8 mile = 220 yards = 1 furlong
    """

    table_name = 'FurlongData'
    path_to_file = cdd_veg_db_tables(table_name + ".pickle")

    if os.path.isfile(path_to_file) and not update:
        furlong_data = load_pickle(path_to_file)
    else:
        try:
            furlong_data = db.read_veg_table(table_name)

            mileage_columns = ['StartMileage', 'EndMileage']  # Re-format mileage data
            furlong_data[mileage_columns] = furlong_data[mileage_columns].applymap(lambda x: str('%.4f' % x))
            furlong_data.set_index(veg_pk(table_name), inplace=True)
            save(furlong_data, db.cdd_veg_db("Tables_original", table_name + ".csv"))

            furlong_data.reset_index(inplace=True)
            # Rename columns
            to_rename_cols = {
                'TEF307601': 'MainSpeciesScore',
                'TEF307602': 'TreeSizeScore',
                'TEF307603': 'SurroundingLandScore',
                'TEF307604': 'DistanceFromRailScore',
                'TEF307605': 'OtherVegScore',
                'TEF307606': 'TopographyScore',
                'TEF307607': 'AtmosphereScore',
                'TEF307608': 'TreeDensityScore'}
            furlong_data.rename(columns=to_rename_cols, inplace=True)
            # Edit the 'TEF' columns
            furlong_data['OtherVegScore'].replace({-1: 0}, inplace=True)
            new_cols = list(to_rename_cols.values())
            furlong_data[new_cols] = furlong_data[new_cols].applymap(lambda x: 0 if pd.np.isnan(x) else x + 1)
            # Re-format date of measure
            dt_fmt = '%d/%m/%Y %H:%M'
            furlong_data['DateOfMeasure'] = furlong_data['DateOfMeasure'].apply(
                lambda x: datetime.datetime.strptime(x, dt_fmt))
            # Edit route data
            furlong_data['Route'] = furlong_data['Route'].replace(get_route_names_dict())

            if set_index:
                furlong_data.set_index(veg_pk(table_name), inplace=True)

            # Make amendment to "CoverPercent" data for which the total is not 0 or 100?
            if pseudo_amendment:
                # Find columns relating to "CoverPercent..."
                colnames = furlong_data.columns
                cp_cols = [x for x in colnames if re.match('^CoverPercent[A-Z]', x)]

                temp = furlong_data[cp_cols].sum(1)
                if not temp.empty:
                    # For all zero 'CoverPercent...'
                    furlong_data.CoverPercentOther.loc[temp[temp == 0].index] = 100.0
                    # For all non-100 'CoverPercent...'
                    idx = temp[~temp.isin([0.0, 100.0])].index

                    nonzero_cols = furlong_data[cp_cols].loc[idx]. \
                        apply(lambda x: x != 0.0). \
                        apply(lambda x: list(pd.Index(cp_cols)[x.values]), axis=1)

                    errors = pd.Series(100.0 - temp[idx])

                    for i in idx:
                        features = nonzero_cols[i].copy()
                        if len(features) == 1:
                            feature = features[0]
                            if feature == 'CoverPercentOther':
                                furlong_data.CoverPercentOther.loc[[i]] = 100.0
                            else:
                                if errors.loc[i] > 0:
                                    furlong_data.CoverPercentOther.loc[[i]] = pd.np.sum([
                                        furlong_data.CoverPercentOther.loc[i], errors.loc[i]])
                                else:  # errors.loc[i] < 0
                                    furlong_data[feature].loc[[i]] = pd.np.sum([
                                        furlong_data[feature].loc[i], errors.loc[i]])
                        else:  # len(nonzero_cols[i]) > 1
                            if 'CoverPercentOther' in features:
                                err = pd.np.sum([furlong_data.CoverPercentOther.loc[i], errors.loc[i]])
                                if err >= 0.0:
                                    furlong_data.CoverPercentOther.loc[[i]] = err
                                else:
                                    features.remove('CoverPercentOther')
                                    furlong_data.CoverPercentOther.loc[[i]] = 0.0
                                    if len(features) == 1:
                                        feature = features[0]
                                        furlong_data[feature].loc[[i]] = pd.np.sum([furlong_data[feature].loc[i], err])
                                    else:
                                        err = pd.np.divide(err, len(features))
                                        furlong_data.loc[i, features] += err
                            else:
                                err = pd.np.divide(errors.loc[i], len(features))
                                furlong_data.loc[i, features] += err

            save_pickle(furlong_data, path_to_file)

        except Exception as e:
            print(e)
            print("Getting '{}' ... Failed.".format(table_name))
            furlong_data = None

    return furlong_data


# Get FurlongLocation
def get_furlong_location(useful_columns_only=True, update=False):
    """
    Note: One ELR&mileage may have multiple 'FurlongID's.
    """

    table_name = 'FurlongLocation'
    path_to_file = cdd_veg_db_tables(table_name + ".pickle")

    if useful_columns_only:
        path_to_file = path_to_file.replace(table_name, table_name + "_cut")

    if os.path.isfile(path_to_file) and not update:
        furlong_location = load_pickle(path_to_file)
    else:
        try:
            # Read data from database
            furlong_location = db.read_veg_table(table_name, index_col=veg_pk(table_name))
            # Re-format mileage data
            mileage_columns = ['StartMileage', 'EndMileage']
            furlong_location[mileage_columns] = furlong_location[mileage_columns].applymap(lambda x: str('%.4f' % x))
            # Save data read from the database
            save(furlong_location, db.cdd_veg_db("Tables_original", table_name + ".csv"))

            # Replace boolean values with binary values
            furlong_location[['Electrified', 'HazardOnly']] = \
                furlong_location[['Electrified', 'HazardOnly']].applymap(int)
            # Replace Route names
            route_names = get_route_names_dict()
            furlong_location['Route'] = furlong_location['Route'].replace(route_names)

            # Select useful columns only?
            if useful_columns_only:
                useful_columns = ['Route', 'DU', 'ELR', 'StartMileage', 'EndMileage', 'Electrified', 'HazardOnly']
                furlong_location = furlong_location[useful_columns]
                # path_to_file = path_to_file.replace(table_name, table_name + "_cut")

            save_pickle(furlong_location, path_to_file)

        except Exception as e:
            print(e)
            print("Getting '{}' ... Failed.".format(table_name))
            furlong_location = None

    return furlong_location


# Get HazardTree
def get_hazard_tree(set_index=False, update=False):
    """
    :param set_index: 
    :param update: 
    :return: 
    """
    table_name = 'HazardTree'
    path_to_file = cdd_veg_db_tables(table_name + ".pickle")

    if os.path.isfile(path_to_file) and not update:
        hazard_tree = load_pickle(path_to_file)
    else:
        try:
            hazard_tree = db.read_veg_table(table_name)
            # Re-format mileage data
            hazard_tree.Mileage = hazard_tree.Mileage.apply(lambda x: str('%.4f' % x))

            save(hazard_tree, db.cdd_veg_db("Tables_original", table_name + ".csv"))

            # Edit the original data
            hazard_tree.drop(['Treesurvey', 'Treetunnel'], axis=1, inplace=True)
            hazard_tree.dropna(subset=['Northing', 'Easting'], inplace=True)
            hazard_tree.Treespecies.replace({'': 'No data'}, inplace=True)

            """
            Note that error data exists in 'FurlongID'. They could be cancelled out when the 'hazard_tree' data set is 
            being merged with other data sets on the 'FurlongID'. Errors also exist in 'Easting' and 'Northing' columns.
            """

            hazard_tree.Route.replace(get_route_names_dict(), inplace=True)  # Replace names of Routes

            # Integrate information from several features in a DataFrame
            def sum_up_selected_features(data, selected_features, new_feature):
                """
                To integrate information from certain columns in a DataFrame
                :param data: [DataFrame] original DataFrame
                :param selected_features: [list] list of columns names
                :param new_feature: [str] new column name
                :return: DataFrame
                """
                data.replace({True: 1, False: 0}, inplace=True)
                data[new_feature] = data[selected_features].fillna(0).apply(sum, axis=1)
                data.drop(selected_features, axis=1, inplace=True)

            # Integrate TEF: Failure scores
            failure_scores = ['TEF30770' + str(i) for i in range(1, 6)]
            sum_up_selected_features(hazard_tree, failure_scores, new_feature='Failure_Score')
            # Integrate TEF: Target scores
            target_scores = ['TEF3077%02d' % i for i in range(6, 12)]
            sum_up_selected_features(hazard_tree, target_scores, new_feature='Target_Score')
            # Integrate TEF: Impact scores
            impact_scores = ['TEF3077' + str(i) for i in range(12, 16)]
            sum_up_selected_features(hazard_tree, impact_scores, new_feature='Impact_Score')
            # Rename the rest of TEF
            work_req = ['TEF3077' + str(i) for i in range(17, 27)]
            work_req_desc = [
                'WorkReq_ExpertInspection',
                'WorkReq_LocalisedPruning',
                'WorkReq_GeneralPruning',
                'WorkReq_CrownRemoval',
                'WorkReq_StumpRemoval',
                'WorkReq_TreeRemoval',
                'WorkReq_TargetManagement',
                'WorkReq_FurtherInvestigation',
                'WorkReq_LimbRemoval',
                'WorkReq_InstallSupport']
            hazard_tree.rename(columns=dict(zip(work_req, work_req_desc)), inplace=True)

            # Note the feasibility of the the following operation is not guaranteed:
            hazard_tree[work_req_desc] = hazard_tree[work_req_desc].fillna(value=0)

            # Rearrange DataFrame index
            hazard_tree.index = range(len(hazard_tree))

            # Add two columns of Latitudes and Longitudes corresponding to the
            # Easting and Northing coordinates
            hazard_tree[['Longitude', 'Latitude']] = hazard_tree[['Easting', 'Northing']].apply(
                lambda x: converters.osgb36_to_wgs84(x.Easting, x.Northing), axis=1)

            save_pickle(hazard_tree, path_to_file)

            if set_index:
                hazard_tree.set_index(veg_pk(table_name), inplace=True)

            hazard_tree.dropna(inplace=True)

        except Exception as e:
            print(e)
            print("Getting '{}' ... Failed.".format(table_name))
            hazard_tree = None

    return hazard_tree


"""
update = True

get_adverse_wind(update)
get_cutting_angle_class(update)
get_cutting_depth_class(update)
get_du_list(index=True, update=update)
get_path_route(update)
get_du_route(update)
get_s8data_from_db_veg(update)
get_tree_age_class(update)
get_tree_size_class(update)
get_tree_type(update)
get_felling_type(update)
get_area_work_type(update)
get_service_detail(update)
get_service_path(update)
get_supplier(update)
get_supplier_costs(update)
get_supplier_costs_area(update)
get_supplier_cost_simple(update)
get_tree_action_fractions(update)
get_veg_surv_type_class(update)
get_wb_factors(update)
get_weed_spray(update)
get_work_hours(update)

get_furlong_data(set_index=False, pseudo_amendment=True, update=update)
get_furlong_location(useful_columns_only=True, update=update)
get_hazard_tree(set_index=False, update=update)
"""

# ====================================================================================================================
""" Get views based on the NR_VEG data """


def make_filename(base_name, route, *extra_suffixes, save_as=".pickle"):
    """
    :param base_name: 
    :param route: 
    :param extra_suffixes: 
    :param save_as: 
    :return: 
    """
    if route is not None:
        route_lookup = get_du_route()
        route = find_match(route, route_lookup.Route)
    # route_suffix = [route] if route is not None else [None]
    filename_base = [base_name] + [route] + [str(s) for s in extra_suffixes]
    filename = "_".join([item for item in filename_base if item]) + save_as
    return filename


# Get vegetation data (75247, 44)
def get_furlong_vegetation_coverage(route=None, update=False):
    """
    :param route: 
    :param update: 
    :return: 
    """
    filename = make_filename("furlong_vegetation_coverage", route)
    path_to_file = cdd_veg_db_views(filename)

    if os.path.isfile(path_to_file) and not update:
        furlong_vegetation_coverage = load_pickle(path_to_file)
    else:
        try:
            furlong_data = get_furlong_data()  # (75247, 39)
            furlong_location = get_furlong_location()  # Set 'FurlongID' to be its index (77017, 7)
            cutting_angle_class = get_cutting_angle_class()  # (5, 1)
            cutting_depth_class = get_cutting_depth_class()  # (5, 1)
            adverse_wind = get_adverse_wind()  # (12, 1)
            # Merge the data that has been obtained
            furlong_vegetation_coverage = furlong_data. \
                join(furlong_location,  # (75247, 46)
                     on='FurlongID', how='inner', lsuffix='', rsuffix='_FurlongLocation'). \
                join(cutting_angle_class,  # (75247, 47)
                     on='CuttingAngle', how='inner'). \
                join(cutting_depth_class,  # (75247, 48)
                     on='CuttingDepth', how='inner', lsuffix='_CuttingAngle', rsuffix='_CuttingDepth'). \
                join(adverse_wind,  # (75247, 49)
                     on='Route', how='inner')

            rte = find_match(route, list(get_route_names_dict().values()))
            if rte is not None:
                furlong_vegetation_coverage = furlong_vegetation_coverage[furlong_vegetation_coverage.Route == rte]

            # The total number of trees on both sides
            tree_no_columns = ['TreeNumberUp', 'TreeNumberDown']
            furlong_vegetation_coverage['TreeNumber'] = furlong_vegetation_coverage[tree_no_columns].sum(1)

            # Edit the merged data
            furlong_vegetation_coverage.drop(
                labels=[f for f in furlong_vegetation_coverage.columns if re.match('.*_FurlongLocation$', f)],
                axis=1, inplace=True)  # (75247, 44)

            furlong_vegetation_coverage.rename(
                columns={'DaysPerFurlongPerYear': 'AdverseWind_DaysPerFurlongPerYear'}, inplace=True)

            furlong_vegetation_coverage.sort_values(by='StructuredPlantNumber', inplace=True)

            # Rearrange index
            furlong_vegetation_coverage.index = range(len(furlong_vegetation_coverage))

            save_pickle(furlong_vegetation_coverage, path_to_file)

        except Exception as e:
            print(e)
            print("Getting '{}' ... Failed.".format(os.path.splitext(filename)[0]))
            furlong_vegetation_coverage = None

    return furlong_vegetation_coverage


# Get data of hazardous tress (22180, 66)
def get_hazardous_trees(route=None, update=False):
    """
    :param route: 
    :param update: 
    :return: 
    """
    filename = make_filename("hazardous_trees_data", route)
    path_to_file = cdd_veg_db_views(filename)

    if os.path.isfile(path_to_file) and not update:
        hazardous_trees_data = load_pickle(path_to_file)
    else:
        try:
            hazard_tree = get_hazard_tree()  # (23950, 59) 1770 with FurlongID being -1
            furlong_location = get_furlong_location()  # (77017, 7)
            tree_age_class = get_tree_age_class()  # (7, 1)
            tree_size_class = get_tree_size_class()  # (5, 1)
            adverse_wind = get_adverse_wind()  # (12, 1)

            hazardous_trees_data = hazard_tree. \
                join(furlong_location,  # (22180, 66)
                     on='FurlongID', how='inner', lsuffix='', rsuffix='_FurlongLocation'). \
                join(tree_age_class,  # (22180, 67)
                     on='TreeAgeCatID', how='inner'). \
                join(tree_size_class,  # (22180, 68)
                     on='TreeSizeCatID', how='inner', lsuffix='_TreeAgeClass', rsuffix='_TreeSizeClass'). \
                join(adverse_wind,  # (22180, 69)
                     on='Route', how='inner'). \
                drop(labels=['Route_FurlongLocation', 'DU_FurlongLocation', 'ELR_FurlongLocation'], axis=1)

            rte = find_match(route, list(get_route_names_dict().values()))
            if rte is not None:
                hazardous_trees_data = hazardous_trees_data.loc[hazardous_trees_data.Route == rte]

            # Edit the merged data
            features = hazardous_trees_data.columns
            hazardous_trees_data.drop(labels=[f for f in features if re.match('.*_FurlongLocation$', f)][:3],
                                      axis=1, inplace=True)  # (22180, 66)
            hazardous_trees_data.rename(columns={'StartMileage': 'Furlong_StartMileage',
                                                 'EndMileage': 'Furlong_EndMileage',
                                                 'Electrified': 'Furlong_Electrified',
                                                 'HazardOnly': 'Furlong_HazardOnly',
                                                 'DaysPerFurlongPerYear': 'AdverseWind_DaysPerFurlongPerYear'},
                                        inplace=True)

            hazardous_trees_data.index = range(len(hazardous_trees_data))  # Rearrange index

            save_pickle(hazardous_trees_data, path_to_file)

        except Exception as e:
            print(e)
            print("Getting '{}' ... Failed.".format(os.path.splitext(filename)[0]))
            hazardous_trees_data = None

    return hazardous_trees_data


# Get vegetation data as well as hazardous trees information (75247, 57)
def get_furlong_vegetation_conditions(route=None, update=False):
    """
    :param route: 
    :param update: 
    :return: 
    """
    filename = make_filename("furlong_vegetation_data", route)
    path_to_file = cdd_veg_db_views(filename)

    if os.path.isfile(path_to_file) and not update:
        furlong_vegetation_data = load_pickle(path_to_file)
    else:
        try:
            hazardous_trees_data = get_hazardous_trees()  # (22180, 66)

            cols = ['ELR', 'DU', 'Route', 'Furlong_StartMileage', 'Furlong_EndMileage']
            furlong_hazardous_trees = hazardous_trees_data.groupby(cols).aggregate({
                # 'AssetNumber': np.count_nonzero,
                'Haztreeid': pd.np.count_nonzero,
                'TreeheightM': [lambda x: tuple(x), pd.np.min, pd.np.max],
                'TreediameterM': [lambda x: tuple(x), pd.np.min, pd.np.max],
                'TreeproxrailM': [lambda x: tuple(x), pd.np.min, pd.np.max],
                'Treeprox3py': [lambda x: tuple(x), pd.np.min, pd.np.max]})  # (11320, 9)

            furlong_hazardous_trees = reset_double_indexes(furlong_hazardous_trees)  # (11320, 14)
            furlong_hazardous_trees.set_index(cols, inplace=True)  # Set index (11320, 9)
            # Rename columns
            furlong_hazardous_trees.rename(columns={'Haztreeid_count_nonzero': 'TreeNumber'}, inplace=True)
            furlong_hazardous_trees.columns = \
                ['Hazard' + x.replace('_a', '_').replace('_<lambda>', '') for x in furlong_hazardous_trees.columns]

            furlong_vegetation_coverage = get_furlong_vegetation_coverage()  # (75247, 44)

            # Processing ...
            furlong_vegetation_data = furlong_vegetation_coverage.join(
                furlong_hazardous_trees, on=['ELR', 'DU', 'Route', 'StartMileage', 'EndMileage'], how='left')
            furlong_vegetation_data.sort_values('StructuredPlantNumber', inplace=True)  # (75247, 53)

            rte = find_match(route, list(get_route_names_dict().values()))
            if rte is not None:
                furlong_vegetation_data = hazardous_trees_data.loc[furlong_vegetation_data.Route == rte]
                furlong_vegetation_data.index = range(len(furlong_vegetation_data))

            save_pickle(furlong_vegetation_data, path_to_file)
        except Exception as e:
            print(e)
            print("Getting '{}' ... Failed.".format(os.path.splitext(filename)[0]))
            furlong_vegetation_data = None

    return furlong_vegetation_data


"""
route = None
update = True

get_furlong_vegetation_coverage(route=None, update=update)
get_hazardous_trees(route=None, update=update)
get_furlong_vegetation_conditions(route=None, update=update)
"""