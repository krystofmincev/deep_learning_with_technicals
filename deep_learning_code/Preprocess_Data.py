#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  6 20:32:45 2017

File for preprocessing data

@author: mincev
"""
import pandas as pd 
import random
import numpy as np
import math
#if in spyder may need to change path to get both helper and tech_calc
from Technicals_Calculator import Technicals_Calculator 
from inspect import signature
from helper import helper

class Preprocess_Data(object):
    """
    Class for preprocessing data. Offeres fucntions for calculationg additonal 
    data points (technicals, z_scores, returns and etc) from DATE, TIME, OPEN, 
    HIGH, LOW, CLOSE, VOL. Additionally offers functions for putting data into 
    batches, and preparing data as [n_steps, n_inputs] if type numpy arrray.
    """
    global FILE_PATH
    FILE_PATH = "/home/mincev/Documents/git/deep_learning_with_technicals/crawler_code/obj/"
    
    def __init__(self, file_name, file_path = FILE_PATH):
        """
        Input:
            file_name (str) = filename to pickle file
            file_path (str) = filepath to pickle file
        """
        self.check_input_types([file_name, file_path], [str, str])
        
        #define variables
        dict_data = helper.load_obj(file_name, file_path)
        self.data_df = self.dict2pandas(dict_data)
        
    def calculate_technicals(self, df, look_back_period = 0):
        """
        Calculates all technicals from Technicals_Calculator:
        [MA(df, n), EMA(df, n), MOM(df, n), ROC(df, n), ATR(df, n), BBANDS(df, n), 
        PPSR(df), STOK(df), STO(df, n), TRIX(df, n), ADX(df, n, n_ADX), MACD(df, n_fast, n_slow),
        MassI(df), Vortex(df, n), KST(df, r1, r2, r3, r4, n1, n2, n3, n4), RSI(df, n), 
        TSI(df, r, s), ACCDIST(df, n), Chaikin(df), MFI(df, n), OBV(df, n), FORCE(df, n), 
        EOM(df, n), CCI(df, n), COPP(df, n), KELCH(df, n), ULTOSC(df), DONCH(df, n), STDDEV(df, n)] 
        
        Note: adjujsts df for missing values resulting from diff caculations
        Input:
            df (pandas df) = df for adding technicals to
            look_back_period (int) = period over which technicals are calculated
                                    if lookback is left as deafualt 0, a random 
                                    value is calculated
        """
        self.check_input_types([df, look_back_period], [pd.core.frame.DataFrame, int])
        
        #define variables
        ##find technicals to calc
        technicals_to_calculate = ['Technicals_Calculator.{0}'.format(f_name) \
                                   for f_name in dir(Technicals_Calculator) \
                                   if f_name[1] != "_"] #get all created functions
        do_not_calculate = ['Technicals_Calculator.KST', 'Technicals_Calculator.TSI', \
                            'Technicals_Calculator.ADX', 'Technicals_Calculator.DONCH',
                            'Technicals_Calculator.ATR'] 
        for do_not_calc in do_not_calculate: #do not calculate these
            technicals_to_calculate.remove(do_not_calc) 
        ##find look for each technical    
        min_look_back, max_look_back = 10, 100
        if look_back_period is 0:
            look_back = [random.randint(min_look_back, max_look_back) \
                         for _ in range(len(technicals_to_calculate))]
        else:
            look_back = [look_back_period for _ in range(len(technicals_to_calculate))]
        
        #execute technicals functions:
        numb_technicals = len(technicals_to_calculate)
        for i, function in enumerate(technicals_to_calculate):
            print("Calculating technical: {0} out of: {1}".format(str(i), str(numb_technicals)))
            technicals_function = eval(function)
            numb_params_in_f = len(signature(technicals_function).parameters)
            try:
                if numb_params_in_f is 1:
                    df = technicals_function(df)
                elif numb_params_in_f is 2:
                    df = technicals_function(df, look_back[i])
                else: 
                    df = technicals_function(df, 20, 50)
            except:
                print('Failed to add data for: {0}'.format(function))
                continue 
        
        #adjust df for missing values:
        max_look_back = max(look_back)
        
        return df[:][max_look_back:] 
    
    def dict2pandas(self, dictionary):
        """
        Function to convest dictionary values into pandas data frame
        Input:
            dictionary (dict) = data as dict
        Output:
            df (pd data frame) = df with cols:
                                 ['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume']
        
        """
        self.check_input_types([dictionary], [dict])
        
        col_index = ['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume']
        df = pd.DataFrame.from_items(dictionary.items(), 
                                     orient='index', 
                                     columns=col_index)
        
        #convert string columns into int
        df = self.cols2int(df)
        
        #sort by date and time
        df = self.sort_df(df, ['Date', 'Time'])
        
        return df
    
    def cols2int(self, df, cols = None):
        """
        Converts data frame cols into numeric types.
        Input:
            df (dataframe) = 
            cols (list) = cols to convert into numeric. If None all are converted
        Output:
            df (dataframe) - Converted
        """
        if cols is None:
            cols = [col for col in list(df.columns.values) if col not in ['Date', 'Time']]
        self.check_input_types([df, cols], [pd.core.frame.DataFrame, list])
        
        for col in cols:
            df[col] = pd.to_numeric(df[col])
        
        return df
    
    def sort_df(self, df, sort_by_cols):
        """
        Function for sorting data frames by cutom cols. We create auxilary cols
        from sort_by_cols, and sort based on these. no more that two cols are
        accepted.
        Input:
            df (dataframe) -
            sort_by_cols (list) = cols for sorting. If two we create an auxilary 
                                  custom col with numbers + digits (col1 + col2)
                                  and sort these
        Output: 
            df (dataframe) - Sorted 
        """
        self.check_input_types([df, sort_by_cols], [pd.core.frame.DataFrame, list])
        assert len(sort_by_cols) < 3
        
        return df.sort_values(sort_by_cols, ascending=True)
    
    def check_input_types(self, function_inputs, input_types):
        """
        Function for testing input types match function desired types
        Input: 
            function_inputs (list) = list of inputs inputed into finction
            input_types (list) = list of function input types 
            Note: lengths of both inputs above must match 
        Output:
            -
        """
        assert type(function_inputs) == type(input_types)
        assert len(function_inputs) == len(input_types)
        
        n_inputs = len(function_inputs)
        try: 
            assert [type(function_inputs[i]) == input_types[i] for i in range(n_inputs)]
        except: 
            print("Function input types do not match desired function inputs")
            
    def calulate_pc_difference(self, df, cols, look_back_period = 1):
        """
        Calculate % difference between values across time
        Input: 
            df (pd dataframe)
            cols (list) = cols to calculate the difference for
            look_back_period (int) = period over which difference is calculated
        Output:
            df 
        """
        self.check_input_types([df, cols, look_back_period], [pd.core.frame.DataFrame, list, int])
        
        for col in cols:
            diff = pd.Series(df[col].pct_change(look_back_period), name = col + "_%diff")
            df = df.join(diff)
        
        return df 
    
    def rolling_normalisation(self, df, col):
        """
        Performs a normal mean min_max standardisation. We use a rolling window 
        to compute these statistics meaning that normalisation only works on
        previously seen data. 
        Input:
            df (pd dataframe) -
            col (str) = column to normalise
        """
        self.check_input_types([df, col], [pd.core.frame.DataFrame, str])
        
        print("\nNormalising data for col: " + col)
        print("This may take a while so please wait...")
        #calculate normalised data
        normalised_data = list()
        length_of_data = len(df)
        min_value = df[col][0] 
        max_value = df[col][0]
        mean_value = df[col][0]
        index_for_mean_cal = 1 #calculate mean at this rolling index to save time
        for i in range(len(df)):
            if i % 10000 is 0: #status 
                print(str(i) + " out of " + str(length_of_data))
            
            data_point = df[col][i]
            if math.isnan(data_point):
                normalised_data.append(data_point)
                index_for_mean_cal = index_for_mean_cal + 2*i
            else:
                try:
                    max_value = self.rolling_max(data_point, max_value)
                    min_value = self.rolling_min(data_point, min_value)
                    if i > index_for_mean_cal:
                        data = df[col][:i]
                        mean_value = np.nanmean(data)
                        #adjust index
                        index_for_mean_cal = index_for_mean_cal*2
                    norm_data_point =  (data_point - mean_value) / (max_value - min_value)
                    normalised_data.append(norm_data_point)
                except:
                    normalised_data.append(0)
        #check that not all values are zero
        assert np.nansum(np.array(normalised_data[:2000])) != 0        
        #add normalised data to pd
        normalised_df_col = pd.DataFrame(normalised_data, columns=[col + '_Norm'], \
                                         index = df.index)
        df = df.join(normalised_df_col)
        
        return df
    
    def rolling_max(self, data_point, previous_max):
        """
        Function for calculating rolling max
        Input: 
            data_point (int) = new data point 
            previous_mac (int) = previous max 
        """
        self.check_input_types([data_point, previous_max], [int, int])
        
        if data_point > previous_max:
            return data_point
        else:
            return previous_max
        
    def rolling_min(self, data_point, previous_min):
        """
        Function for calculating rolling min
        Input: 
            data_point (int) = new data point 
            previous_min (int) = previous min 
        """
        self.check_input_types([data_point, previous_min], [int, int])
        
        if data_point < previous_min:
            return data_point
        else:
            return previous_min
    
    def handle_nan(self, df, replace_nan_with = 0):
        """
        Replace nans with 'replace_nan_with'.
        Input: 
            df (pd dataframe) 
            replace_nan_with (int) = replace nans with this value
        Output:
            df 
        """
        self.check_input_types([df, replace_nan_with], [pd.core.frame.DataFrame, int])
        
        #check for nans and replace all with 'replace_nan_with'
        data_frame_col_names = df.columns.values.tolist()
        for col in data_frame_col_names:
            if df[col].isnull().values.any():
                df[col].fillna(replace_nan_with, inplace=True)
            #check that everything was converted
            assert df[col].isnull().values.any() == False
        return df
   
        
if __name__ == "__main__":
    #define variables:
    diff_cols = ['Open', 'High', 'Low', 'Close']
    file_name = "{0}_2014_2017"
    
    #prepare technicals files
    for i in range(2, 46):
        if i is 26: #file missing
            continue
        #load in pickle data
        file = file_name.format(str(i))
        preprocess_data = Preprocess_Data(file)
        data_df = preprocess_data.data_df
        
        #add columns to data_df
        ##calculate % difference for ['Open', 'High', 'Low', 'Close']
        data_df = preprocess_data.calulate_pc_difference(data_df, diff_cols)
        ##add technicals cols
        data_df = preprocess_data.calculate_technicals(data_df)
        
        #format data
        ##normalize data
        for col in diff_cols:
            data_df = preprocess_data.rolling_normalisation(data_df, col)
        ##handle nans in cols
        data_df = preprocess_data.handle_nan(data_df)
        
        #create dictionary with xs and ys [use data frames to store values]
        y_cols = ['Open_%diff', 'Close_%diff']
        y = data_df[y_cols][1:] #do not include 1st value (focus on t+1)
        x_cols = [col for col in data_df.columns.values.tolist() if col not in diff_cols]
        x = data_df[x_cols][:-1] #do not add last value because x is t and y t+1
        assert len(y) == len(x) #test condition
        
        #save data as dict 
        helper.save_obj(file, dict({'Xs': x, 'Ys': y}))