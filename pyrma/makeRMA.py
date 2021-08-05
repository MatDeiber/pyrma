"""
Create RMA2 and RMA11 setup files for a range of years based on a template
for the first year

"""

#Authors: Mathieu Deiber <m.deiber@wrl.unsw.edu.au>

import calendar
import os
from datetime import datetime

class MakeRMA:
    """
    Create RMA2 and RMA11 setup files for a range of years based on a template
    for the first year
    
    ...
    Attributes
    ----------
    template_list:list
        list of all the lines in the template
    first_year:int
        first year
    type: str
        type of RMA model (RMA2 or RMA11)
    runNumber: str
        string to identify the simulation
        

  
    Methods
    -------

    get_start_year(self)
       get the year from the template
    generate_rm2(output_dir = 'runfiles',start_date,end_date, timestep = 0.25)
       generate rm2 setup files
    generate_r11(output_dir = 'runfiles',start_date,end_date, timestep = 0.25)
       generate rm11 setup files
    
    

    """
    def __init__(self,template,runNumber = 'ABC001'):
        """
        Parameters
        ----------
        template : str
           name of the rma setup file to use as a template
        runNumber : str
           string to identify the simulation
        """ 
        self.template_list = open(template,'r').readlines()
        self.first_year = self.get_start_year()
        self.type = template.split('.')[-1]
        self.runNumber = runNumber
        
    def get_start_year(self):
        """
        method used to get the year from the template

        """ 
        for line in self.template_list:
            if line[:3] == 'C1 ':
                return int(line.split()[3])
            
    def generate_rm2(self,start_date,end_date, output_dir = 'runfiles', timestep = 0.25):
        """
        Parameters
        ----------
        output_dir: str, optional - default 'runfiles'
            folder to save the setup files
        start_date: datetime
            datetime object of first day included in the simulation
        end_date: datetime
            datetime object of last day included in the simulation
        timestep: float
            computational timestep (in h)
        """ 
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        start_year = start_date.year
        start_day = start_date.timetuple().tm_yday
        end_year = end_date.year
        end_day = end_date.timetuple().tm_yday
        
        years = range(start_year, end_year + 1)
        
        for year in years:
            f = open('{}/{}_{}.rm2'.format(output_dir,self.runNumber,year),'w')
            
            endfill = False
            endlimit = False
           
            if year != end_year:
                
                n_steps = int(1/timestep * 24 * 365) 
                n_days = 365
                if calendar.isleap(year):
                    n_steps += int(24/timestep)
                    n_days += 1
            else:
                n_steps = int(1/timestep * 24 * end_day) 
                n_days = end_day
            
            for line in self.template_list:
                line = line.strip()
                
                if not endfill:
                    if (line[:7] == 'INBNRST') and year != self.first_year:
                        f.write('INBNRST   {}_{}.rst\n'.format(self.runNumber,year - 1))
                    else:
                        f.write('{}\n'.format(line.replace(str(self.first_year), str(year))))
                        if line[:6] == 'ENDFIL':
                            endfill = True
                elif not endlimit:
                    f.write('{}\n'.format(line))
                    if line[:8] == 'ENDLIMIT':
                        endlimit = True
                else:
                    if line[:3] == 'C1 ':
                        f.write('{}\n'.format(line.replace(str(self.first_year), str(year))))
                    elif line[:3] ==  'C3 ':
                        f.write('{}{:>8.0f}{}\n'.format(line[:32],n_steps,line[40:]))
                    elif line[:3] ==  'AUT':
                        f.write('{}{:>8.0f}{:>8.0f}{}\n'.format(line[:24],year,n_days,line[40:]))
                    elif line[:3] ==  'DT ':
                        if len(line) < 25:
                            f.write('{}\n'.format(line))
                        else:
                            f.write('{}{:>8.3f}{}{:>8.0f}{:>8.0f}{}\n'.format(line[:8],timestep,line[16:24],year,n_days,line[40:]))      
                    else:
                        f.write('{}\n'.format(line))
            f.close()
                        
       
    def generate_r11(self,start_date,end_date, output_dir = 'runfiles', timestep = 0.25):
        """
        Parameters
        ----------
        output_dir: str, optional - default 'runfiles'
            folder to save the setup files
        start_date: datetime
            datetime object of first day included in the simulation
        end_date: datetime
            datetime object of last day included in the simulation
        timestep: float
            computational timestep (in h)
        """ 
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        start_year = start_date.year
        start_day = start_date.timetuple().tm_yday
        end_year = end_date.year
        end_day = end_date.timetuple().tm_yday
        
        years = range(start_year, end_year + 1)
        
        for year in years:
            f = open('{}/{}_{}.r11'.format(output_dir,self.runNumber,year),'w')
            
            endfill = False
            endlimit = False
           
            if year != end_year:
                
                n_steps = int(1/timestep * 24 * 365) 
                n_days = 365
                if calendar.isleap(year):
                    n_steps += int(24/timestep)
                    n_days += 1
            else:
                n_steps = int(1/timestep * 24 * end_day) 
                n_days = end_day
            
            for line in self.template_list:
                line = line.strip()
                
                if (line[:7] == 'INBNRST') and year != start_year:
                    f.write('INBNRST   {}_{}_WQ.rst\n'.format(self.runNumber,year - 1))
                elif not endfill:
                    line = line.replace(str(start_year), str(year))
                    f.write('{}\n'.format(line))
                    if line[:6] == 'ENDFIL':
                        endfill = True
                elif not endlimit:
                    f.write('{}\n'.format(line))
                    if line[:8] == 'ENDLIMIT':
                        endlimit = True
                else:
                    if line[:3] == 'C0 ':
                        line = line.replace(str(start_year), str(year))
                        f.write('{}\n'.format(line))
                    elif line[:3] ==  'C3 ':
                        f.write('{}{:>8.0f}{}\n'.format(line[:24],n_steps,line[32:]))
                    elif line[:3] ==  'DT ':
                        f.write('{}{:>8.3f}{:>8.0f}{:>8.0f}    24.0\n'.format(line[:8],timestep,year,n_days))      
                    else:
                        f.write('{}\n'.format(line))
            f.close()
    
        