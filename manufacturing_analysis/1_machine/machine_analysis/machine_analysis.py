import sys
import os
import time
import pandas as pd
from datetime import datetime
import numpy as np

class MachineAnalysis:
    def __init__(self, df, ts, fields, div_col1, div_col2, div_col3):
        self.df = df
        self.div_col1 = div_col1
        self.div_col2 = div_col2
        self.div_col3 = div_col3
        self.fields = fields.split('|')
        self.ts = ts
        
        
    def statis(self, div_df):
        div_df = div_df.reset_index(drop=True)
        
        try:
            dist = []
            x = div_df['absolute_x']
            y = div_df['absolute_y']
            z = div_df['absolute_z']
            feed = div_df['feed_rate']
            
            for i in range(len(div_df)):
                if i > 0:
                    a = np.array((x[i], y[i], z[i]))
                    b = np.array((x[i-1], y[i-1], z[i-1]))
                    val = np.sqrt(np.sum(np.square(a-b)))
                else:
                    val = 0

                dist.append(val)
            div_df['dist'] = pd.Series(dist)
        except:
            print('error!')
            exit(1)
        
        try:
            temp_dict = dict()
            temp_dict[self.div_col1] = list(div_df[self.div_col1].unique())[0]
            temp_dict[self.div_col2] = list(div_df[self.div_col2].unique())[0]
            temp_dict[self.div_col3] = list(div_df[self.div_col3].unique())[0]
            ts_list = div_df[self.ts].to_list()
            temp_dict['start_time'] = ts_list[0]
            temp_dict['end_time'] = ts_list[-1]
            temp_dict['operation_time_sec'] = len(div_df)
            temp_dict['dist_sum'] = div_df['dist'].sum()
            temp_dict['dist_mean'] = div_df['dist'].mean()
            for col in self.fields:
                temp_dict['{}_sum'.format(col)] = div_df[col].sum()
                temp_dict['{}_mean'.format(col)] = div_df[col].mean()
        except:
            print(div_df)
            exit(0)
            
        return temp_dict
    
    
    def divide_sort(self):
        statis_list = []
        
        # device_id_list = list(self.df[self.div_col1].unique())
        # devid_df_list = []
        # partnum_df_list = []
        # partscount_df_list = []

        # for _id in device_id_list:
        #     device_id_df = self.df.query("%s == '%s'" %(self.div_col1, _id))
        #     devid_df_list.append(device_id_df)

        # for devid_df in devid_df_list:
        #     part_num_list = list(devid_df[self.div_col2].unique())
        #     for _part_num in part_num_list:
        #         part_num_df = devid_df.query("%s == %s" %(self.div_col2, _part_num))
        #         partnum_df_list.append(part_num_df)

        # for partnum_df in partnum_df_list:
        #     part_count_list = list(partnum_df[self.div_col3].unique())
        #     for _part_count in part_count_list:
        #         part_count_df = partnum_df.query("%s == %s" %(self.div_col3, _part_count))
        #         statis_list.append(self.statis(part_count_df))
                
        device_id_list = list(self.df[self.div_col1].unique())

        for _id in device_id_list:
            device_id_df = self.df.query("%s == '%s'" %(self.div_col1, _id))
            part_num_list = list(device_id_df[self.div_col2].unique())
            for _part_num in part_num_list:
                part_num_df = device_id_df.query("%s == %s" %(self.div_col2, _part_num))
                part_count_list = list(part_num_df[self.div_col3].unique())
                for _part_count in part_count_list:
                    part_count_df = part_num_df.query("%s == %s" %(self.div_col3, _part_count))
                    statis_list.append(self.statis(part_count_df))
        
        return statis_list