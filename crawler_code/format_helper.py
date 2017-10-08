#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 30 01:38:56 2017

@author: mincev
"""
import csv
import os

class format_helper(object):
    """
    Class providing methods for formatting csv files
    """
    
    def list2dic(self, list_obj, col_key, start_index, col_key_2 = -1, 
                 dic = {}, dic_key_set = set()):
        """
        Function to transform list into dic. The dic key is the value 
        found in col_key, with values after this added to the dic under the
        dic key 
        Input: 
            list_obj (list of lists) -
            col_key (int) = index for dic_key (start from 0)
            start_index (int) = index for starting values to be added to dict
            col_key_2 (int) = if second key required to form merged key
            dic (dict) = default dictionary to add list to
            dic_key_set (set) = default set fro dict keys
        Output:
            dic (dict) = dictinary wih key (date-time) and read in data
            dic_key_list (set) = list of dic keys (date-time)
        """
        assert type(list_obj) and type(list_obj[0]) is list
        assert type(col_key) and type(start_index) and type(col_key_2) is int 
        assert type(dic) is dict
        assert type(dic_key_set) is set
        assert len(list_obj[0]) >= col_key
        
        print("Converting list to dictionary")
        dic_key_index = [col_key]
        if col_key_2 is not -1:
            dic_key_index.append(col_key_2)
        
        for i in range(len(list_obj)):
            dic_key = '-'.join([str(list_obj[i][j]) for j in dic_key_index])
            dic[dic_key] = list_obj[i][start_index:]
            dic_key_set.add(dic_key)
            
        return dic, dic_key_set
    
    def read_in_csv_data(self, filename, delimiter = ";"):
        """
        Funtion to read in csv data allowing for different delimiters 
        Input:
            filename (str) = name of file with directory to read in 
            delimiter (str) = eg: [';', ',', ' '] 
        Output: 
            data = csv data as list without header
        """
        assert type(filename) and type(delimiter) is str 
        with open(filename, 'r') as csv_file:
            reader = csv.reader(csv_file, delimiter=delimiter)
            data = list(reader)[1:]
        
        #check that data was read in correctly -> len(row) is not 1
        try:
            assert len(data[0]) is not 1 
            return data
        except:
            print("Data not read-in correctly with {0} delimiter".format(delimiter))
            return None 
    
    def merge_csvs(self, file_names, file_path = "/home/mincev/Downloads/", \
                     col_key = 2, start_index = 4, col_key_2 = 3):
        """
        Function for merging two csvs with the same columns into a dictionary 
        Input:
            file_names (list str) = list of filenames without '.csv'
            file_path (str) = path to files (must both be in same directory)
            col_key (int) = index for dic_key (start from 0)
            start_index (int) = index for starting values to be added to dict
            col_key_2 (int) = if second key required to form merged key
        Output: 
            dic (dict) = dictionary of merged values 
            dic_key_list = key to dictionary
        """
        assert type(file_names) is list
        assert len(file_names) > 1
        assert type(file_names[0]) and type(file_path) is str
        assert type(col_key) and type(start_index) and type(col_key_2) is int
        if len(file_names[0]) > 4: assert file_names[0][-4:] != '.csv'
         
        #check that file exists
        files = []
        for file in file_names:
            full_file_name = file_path + file + '.csv'
            try:
                assert os.path.isfile(full_file_name)
                files.append(full_file_name)
            except:
                print("No file of name: {0}\n".format(full_file_name))
        
        data = []
        number_of_files = len(files)
        for i in range(0, number_of_files):
            for delimiter in [';', ',', ' ']:
                #find correct delimiter
                #Some files may use ; or , .... and so may need different reader
                read_in_data = self.read_in_csv_data(files[i], delimiter = delimiter)
                if read_in_data is not None:
                    break
            try:
                assert len(read_in_data[0]) >= col_key
                data.append(read_in_data) # append data without header
            except: #if break never exceuted
                print("problem downloading data")
        
        #store data values in dic 
        dic = {} 
        dic_key_set = set()
        for i in range(0, number_of_files):
            dic, dic_key_set = self.list2dic(data[i], col_key, start_index, col_key_2, 
                                              dic, dic_key_set)
            
        return dic, list(dic_key_set)
