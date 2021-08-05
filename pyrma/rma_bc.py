"""
Read and Update RMA Modelling Suite input ELT and WQG boundary files

"""
#Authors: Mathieu Deiber <m.deiber@wrl.unsw.edu.au>
       

import pandas as pd
import os
from datetime import timedelta, datetime
import re

class RMA_bc:
    """
    Read RMA results files step by step
    
    ...
    Attributes
    ----------
    df: dataframe
       dataframe of the flow of the ELT or WQG file
    elements: list of int
      list of all the elements included in the ELT or WQG file
    constituents: list of str
       list of all the constituents
    df_wq_dict: dict of dataframe
       key: constituents
       dataframe of the concentration for each constituent
    type_dict: dict of int
       key: element number
       element type

    
    Methods
    -------
    read_elts(filenames)
       read an *.elt file
    read_wqgs(filenames,constituents)
       read a *.wqg file
    update_elts(df)
       update df attribute
    update_wqgs(dfs_dict, reset = False)
       update df_wq_dict attribute
    get_elements()
        get list of elements
    get_constituents()
        get list of constituents
    create_elts(output_dir='output_bc')
        save to elt file
    create_wqgs(output_dir='output_bc')
       save to wqg file
    """
    
    def __init__(self):
        self.df = pd.DataFrame()
        self.elements = []
        self.constituents = []
        self.df_wq_dict = {}
        self.type_dict = {}
        
    def read_elts(self, filenames):    
        """
        Parameters
        ----------
        filenames : list of str
            List of all the elt files
        """        
        for filename in filenames:
            print('Processing File {}'.format(filename))
            df2  = pd.DataFrame()
            with open(filename) as f:
                content = [x.strip() for x in f.readlines()]
            
            for c in content:
                try:
                    lineType = c[:3]
                except:
                    lineType = 'NOTHING'
        
                if lineType == 'QEI':
                    elemTemp = int(c[3:16])
                    yearTemp = int(c[25:32])

                elif lineType == 'QE ':
                    dayTemp = int(c[3:8])
                    hourTemp = int(c[8:16])
                    flowTemp = float(c[16:24])
                    dateTemp = datetime(yearTemp,1,1) + timedelta(hours = hourTemp) + timedelta(days = dayTemp - 1)
                    df2.loc[dateTemp,elemTemp] = flowTemp
                elif lineType == 'END':
                    break
            if filename == filenames[0]:
                self.df = df2
            else:
                self.df = self.df.append(df2)
        self.elements = [*self.df]
        #return self.df
    
    def read_wqgs(self,filenames,constituents):
        """
        Parameters
        ----------
        filenames : list of str
            List of all the wqg files
        constituents : list of str
            List of all the constituents (should be consistent with the order
            in the wqg file)
        """    
        
        self.constituents  = constituents

        #column_name = ['PORGN','DORGN','NH3','NO2','NO3','PORGP','DORGP','PO4','PIP','PORGC','DORGC','TIC','DO','TEMP','SALIN','ZOOP','MZOOP','ALG1','ALG2','COLIF','SSED']
        for filename in filenames:
            with open(filename) as f:
                content = [x.strip() for x in f.readlines()]
            for c in content:
                try:
                    lineType = c[:3]
                except:
                    lineType = 'NOTHING'    
                    
                if lineType == 'QT ':
                    elemTemp = int(c[3:16])
                    inflowTypeTemp = int(c[16:24])
                    if inflowTypeTemp == 1:
                        elemTemp = -elemTemp
                    yearTemp = int(c[24:32])
                    if elemTemp not in self.df_wq_dict:
                        self.df_wq_dict[elemTemp] = pd.DataFrame(columns = self.constituents)
                        self.type_dict[elemTemp] = inflowTypeTemp

                    
                elif lineType == 'QD ':
                    dayTemp = int(c[3:8])
                    hourTemp = int(c[8:16])
                    dateTemp = datetime(yearTemp,1,1) + timedelta(hours = hourTemp) + timedelta(days = dayTemp - 1)
                    
                    if inflowTypeTemp == 3:          
                        flowTemp = float(c[16:24])
                        if inflowTypeTemp != 1:
                            self.df.loc[dateTemp,elemTemp] = flowTemp
                        concentrationsTemp = re.findall('........',c[24:])
                    elif inflowTypeTemp == 1:
                        concentrationsTemp = re.findall('........',c[16:])
                        
                    concentrationsTemp = [float(c) for c in concentrationsTemp]
                    
                    self.df_wq_dict[elemTemp].loc[dateTemp] = concentrationsTemp
        
        self.elements = [*self.df_wq_dict]
        
    
    def update_elts(self,df):
        """
        Parameters
        ----------
        df : dataframe
            update the flow dataframe
        """        
        self.df = df
        self.elements = [*self.df]
    
    def update_wqgs(self,dfs_dict, reset = False):
        
        """
        Parameters
        ----------
        dfs_dict : dict of dataframe
            update the constituents dataframes
            
        reset: Bool, optional default set to False
            option to overwrite df_wq_dict attribute (instead of updating)
           
        """                
        if reset:
            self.df_wq_dict = dfs_dict
        else:
            for key,val in dfs_dict.items():
                self.df_wq_dict[key] = val
            
    
    def get_elements(self):
        """
        Returns
        ----------
        list of elements
        """        
        return self.elements
    
    def get_constituents(self):
        """
        Returns
        ----------
        list of constituents
        """       
        return self.constituents
    
    def create_elts(self,output_dir='output_bc'):
        """
        Parameters
        ----------
        output_dir : str (default: 'output_bc')
            name of the folder to save the elt files
        """        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        startyear = self.df.index[0].year
        endyear = self.df.index[-1].year
        years = range(startyear,endyear+1)
        for year in years:
            with open('{}/{}.elt'.format(output_dir,year),'w') as f:
                f.write('TE      BC GENERATED - {}\n'.format(datetime.now()))
                for element in self.elements:
                    f.write('QEI{:>13}       1{:>8}\n'.format(element,year))            
                    mask = self.df.index.year == year
                    data = self.df.loc[mask][element]
                    
                    day = data.index.dayofyear
                    
                    for i,d in data.items():
                        f.write('QE{:>6}{:>8}{:>+8.1E}\n'.format(i.dayofyear,i.hour,d))
                        
                f.write('ENDDATA')
                
    def create_wqgs(self,output_dir='output_bc'):
        """
        Parameters
        ----------
        output_dir : str (default: 'output_bc')
            name of the folder to save the wqg files
        """       
        #ideas to improve, convert each row to string before processing. using list comprehension
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        startyear = self.df.index[0].year
        endyear = self.df.index[-1].year
        years = range(startyear,endyear+1)
        
        for year in years:
            with open('{}/{}.wqg'.format(output_dir,year),'w') as f:
                for element,type_el in self.type_dict.items():
                    f.write('TI      Elements {}\n'.format(element))
                    f.write('{:<8}{:>8}{:>8}{:>8}\n'.format('QT',element,abs(type_el),year))            
                    mask = self.df_wq_dict[element].index.year == year
                    data_wq= self.df_wq_dict[element].loc[mask]  
                    
                    for i,row in data_wq.iterrows():
                        
                        if type_el != 1:
                            flow = self.df.loc[i,element]
                            f.write('{:<5}{:>3}{:>8}{:>+8.1E}'.format('QD',i.dayofyear,i.hour,flow))
                        else:
                            f.write('{:<5}{:>3}{:>8}'.format('QD',i.dayofyear,i.hour))
                        
                        for constituent in row:

                            f.write('{:>8.2E}'.format(constituent))
                            
                        f.write('\n')
                        
                        
                f.write('ENDDATA')
    
        
        
        
                
        