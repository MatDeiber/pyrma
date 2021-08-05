"""
Convert a list of RMA Modelling Suite (RMA-2, RMA-11 and RMA-10) result files 
(*.rma) to csv.

"""

#Authors: Mathieu Deiber <m.deiber@wrl.unsw.edu.au>


from .rma import RMA
from datetime import datetime, timedelta
import numpy as np
from .mesh import Mesh
import pandas as pd
from datetime import datetime, timedelta

class ProcessRMA:
    """
    Read RMA results files step by step
    
    ...
    Attributes
    ----------
    filenames: list of str
       list of all the files to process
    nodes: list of int
       list of all the nodes


    
    Methods
    -------
    update_nodes(self,nodes)
       update the nodes attribute
    rma2_to_csv(output_name,parameters = ['xvel','yvel','depth','elevation'])
       save rma2 result files into a csv file
    rma11_to_csv(output_name,dict_constituents = {'SALINITY':1})
       save rma11 result files into a csv file
    rma10_to_csv(output_name,parameters = ['xvel','yvel','zvel',
                    'depth','elevation','salinity','temperature','sussed'])
       save rma10 result files into a csv file
    makeRaster(mesh_name,filenames,parameter,percentiles,bins=(60,60)) (static method)

    """    
    def __init__(self,filenames, nodes):
        """
        Parameters
        ----------
        filenames : list of str
            List of all the rma files
        nodes : list of int
            List of all the nodes number to extract data
        """ 
        self.filenames = filenames
        self.nodes = nodes
        
    def update_nodes(self,nodes):
        """
        Parameters
        ----------
        nodes : list of int
            List of all the nodes number
        """ 
        self.nodes = nodes
    
    def rma2_to_csv(self,output_name,parameters = ['xvel','yvel','depth','elevation']):    
        """
        Parameters
        ----------
        output_name : str
            List of all the elt files
        parameters: list of str
            List of all the parameters to save
        """ 
        pre = output_name[:-4]
        suf = output_name[-4:]
        fnames_dict = {'xvel':'{}_xvel{}'.format(pre,suf),
                  'yvel':'{}_yvel{}'.format(pre,suf),
                  'depth':'{}_depth{}'.format(pre,suf),
                  'elevation':'{}_elevation{}'.format(pre,suf)
                }
        fnames = {}
        for param in parameters:
            fnames[param] = open(fnames_dict[param],'w')
            fnames[param].write('Date,{}\n'.format(','.join(map(str,self.nodes))))
                
        for filename in self.filenames:
            R=RMA(filename)

            while R.next():
                date_step = datetime(R.year,1,1) + timedelta(hours = R.time)
                for param in parameters:   
                    param_val = getattr(R,param)
                    param_nodes = [param_val[n] for n in self.nodes]
                    fnames[param].write('{},{}\n'.format(date_step,','.join(map(str,param_nodes))))
                    
        for param in parameters:
            fnames[param].close()
            
                
    def rma11_to_csv(self,output_name,dict_constituents = {'SALINITY':1}):
        """
        Parameters
        ----------
        output_name : str
            List of all the elt files
        dict_constituents: dict
            dictionary linking constituent name and number to be output
        """ 
        pre = output_name[:-4]
        suf = output_name[-4:]
        
        list_constituents_name = [name for name,val in dict_constituents.items()]
        fnames_dict = {}
        for name,val in dict_constituents.items():
            fnames_dict[name] = '{}_{}{}'.format(name,pre,suf)

        fnames = {}
        for param in list_constituents_name:
            fnames[param] = open(fnames_dict[param],'w')
            fnames[param].write('Date,{}\n'.format(','.join(map(str,self.nodes))))
                
        for filename in self.filenames:
            R=RMA(filename)

            while R.next():
                date_step = datetime(R.year,1,1) + timedelta(hours = R.time)
                for param,val in dict_constituents.items():   
                    param_val = R.constit[val]
                    param_nodes = [param_val[n] for n in self.nodes]
                    fnames[param].write('{},{}\n'.format(date_step,','.join(map(str,param_nodes))))
                    
        for key,val in fnames.items():
            val.close()
    
    def rma10_to_csv(self,output_name,parameters = ['xvel','yvel','zvel',
                    'depth','elevation','salinity','temperature','sussed']):
        """
        Parameters
        ----------
        output_name : str
            List of all the elt files
        parameters: list of str
            List of all the parameters to save
        """ 
        pre = output_name[:-4]
        suf = output_name[-4:]
        fnames_dict = {'xvel':'{}_xvel{}'.format(pre,suf),
                  'yvel':'{}_yvel{}'.format(pre,suf),
                  'zvel':'{}_zvel{}'.format(pre,suf),
                  'depth':'{}_depth{}'.format(pre,suf),
                  'elevation':'{}_elevation{}'.format(pre,suf),
                  'salinity':'{}_salinity{}'.format(pre,suf),
                  'temperature':'{}_temperature{}'.format(pre,suf),
                  'sussed':'{}_sussed{}'.format(pre,suf)
                }
        fnames = {}
        for param in parameters:
            fnames[param] = open(fnames_dict[param],'w')
            fnames[param].write('Date,{}\n'.format(','.join(map(str,self.nodes))))
                
        for filename in self.filenames:
            R=RMA()
            R.open(filename)

            while R.next():
                date_step = datetime(R.year,1,1) + timedelta(hours = R.time)
                for param in parameters:   
                    param_val = getattr(R,param)
                    param_nodes = [param_val[n] for n in self.nodes]
                    fnames[param].write('{},{}\n'.format(date_step,','.join(map(str,param_nodes))))
                    
        for param in parameters:
            fnames[param].close()
            