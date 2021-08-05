"""
Read and Update RMA mesh file (ASCII format)

"""

#Authors: Mathieu Deiber <m.deiber@wrl.unsw.edu.au>



import numpy as np
import re

class Mesh:
    """
    Read RMA results files step by step
    
    ...
    Attributes
    ----------
    df: dataframe
       dataframe of the flow of the ELT or WQG file
    self.name
    self.elements = {}
    self.elements_type = {}
    self.nodes = {}
    self.elements_1D = []
    self.elements_2D = []
    self.lines
    self.nodes[n] = {}

    
    Methods
    -------
    read_elts(filenames)
       read an *.elt file

    xy_to_node(x,y,reach = None)
        return the nearest node number
        
    closest_node(node, nodes)
        method to calculate the distance between one node and a list of nodes
        
    update_channel_width(val = 1, method = 'constant', element_type = [1])
        method to update 1D channel width
        
    get_nodes()
        return a list of nodes
        
    update_depth(depth = {})
        update the depth
        
    save_mesh(output='new_mesh.rm1')
       save the mesh


    """
    def __init__(self, filename):
        """
        Parameters
        ----------
        filename : str
            name of the meshfile to import
        """ 
        self.name = filename
        self._process_meshfile()
        
    def _process_meshfile(self):
        """
        method to process the meshfile
        
        """ 
        self.elements = {}
        self.elements_type = {}
        self.nodes = {}
        self.elements_1D = []
        self.elements_2D = []
        
        with open(self.name,'r') as f:
            self.lines = f.readlines()
        
        elementSection = True
        nodeSection = False    
        for idx, l in enumerate(self.lines[3:]):
            
            if elementSection and len(l) > 6:
                element_number = int(l[:5])
                nodes_number = re.findall('.....',l[5:45])

                nodes = list(map(int, nodes_number))
                nodes = [node for node in nodes if node > 0]
                self.elements[element_number] = nodes
                self.elements_type[element_number] =int(l[45:50])
               
            elif elementSection and l[:5] == ' 9999':
                elementSection = False
                nodeSection = True
                self.end_elementSection = idx + 3
                
            elif nodeSection and len(l) > 11:
                n,x,y,z = l.split()[:4]
                n,x,y,z = int(n), float(x), float(y), float(z)
                channel = l[60:120].split()
                
                self.nodes[n] = {}
                self.nodes[n]['x'] = x
                self.nodes[n]['y'] = y
                self.nodes[n]['z'] = z
                
                if len(channel) > 0:
                    self.nodes[n]['channel'] = [float(c) for c in channel]
                

            if nodeSection and  l[:10] == '      9999':
                nodeSection = False
                self.end_nodeSection = idx + 3
                break
            
        self.elements_list = list(self.elements.keys())
        self.nodes_list = list(self.nodes.keys())
        
        for element in self.elements_list:
            
            if self.elements_type[element] > 100:
                continue
            
            if len(self.elements[element]) <= 3:
                self.elements_1D.append(element)
            else:
                self.elements_2D.append(element)
        
    def xy_to_node(self,x,y,reach = None):
        """
        Parameters
        ----------

        x : float
            x coordinate
        y : float
            y coordinate
        reach : int, optional
            element type number to look for the nearest node
            
            
        Returns
        -------
            return the number of the nearest node
        """ 
        
        
        node_list = set()
        if reach:
            for element, nodes in self.elements.items():
                node_list.update(self.elements[element])
        else:
            node_list.update(self.nodes_list)
        node_list = list(node_list)
            
        nodes = np.array([np.array([self.nodes[node]['x'],self.nodes[node]['y']]) for node in node_list])
        idx = self.closest_node(np.array([x,y]), nodes)
        
        return node_list[idx]
            
        
                
    def closest_node(self,node, nodes):
        """
        Parameters
        ----------
        node : array
            numpy array of dim 2
        nodes : array
            numpy array of numpy array 
            
        Returns
        -------
        return the index of the nearest node
        """ 
        nodes = np.asarray(nodes)
        dist_2 = np.sum((nodes - node)**2, axis=1)
        return np.argmin(dist_2)

            
    
    def update_channel_width(self,val = 1, method = 'constant', element_type = [1]):
        """
        Parameters
        ----------
        val : float
            width factor
            
        method: str
            string to indicate which method to use to change the witdh of the channel
            
        element_type: list of int
            list of the element types included in the transformation 
        """ 
        #method: constant or factor
        node_list = set()
        for element in self.elements:
            if (element in self.elements_1D) and (self.elements_type[element] in element_type):
                node_list.update(self.elements[element])
                
        for node in node_list:
            if method == 'factor':
                self.nodes[node]['channel'][0] = self.nodes[node]['channel'][0] * val                
            elif method == 'constant':
                self.nodes[node]['channel'][0] = self.nodes[node]['channel'][0] + val
            else:
                print('The method: {} is not implemented - select \'factor\' or \'constant\''.format(method))
                
    
    def get_nodes(self):
        """
        return a list of all the nodes in the mesh
        """ 
        return self.nodes
    
    def update_depth(self, depth = {}):
        """
        Parameters
        ----------
        depth : dict
            dict of the node:depth to be updated
        """ 
        
        for node, val in depth.items():
                self.nodes[node]['z'] = val
                
    def save_mesh(self, output='new_mesh.rm1'):
        """
        Parameters
        ----------
        output : str
            name of the output file
        """ 
        with open(output,'w') as f:
            for line in self.lines[:self.end_elementSection + 1]:
                f.write(line)
            self._make_node_lines()
            for line in self.nodes_lines:
                f.write(line)
            for line in self.lines[self.end_nodeSection:]:
                f.write(line)
                
                
    def _make_node_lines(self):
        """
        method to format the node lines
        """ 
        self.nodes_lines = []
        for node in self.nodes_list:
            if 'channel' in self.nodes[node]:
                self.nodes_lines.append('{:>10.0f}{:>16.3f}{:>20.3f}{:>14.3f}{:>10.2f}{:>10.2f}{:>10.2f}{:>10.2f}{:>10.2f}{:>10.2f}         0    0.0000\n'.format(
                        node,self.nodes[node]['x'],self.nodes[node]['y'],self.nodes[node]['z'],*self.nodes[node]['channel']))
            else:
                self.nodes_lines.append('{:>10.0f}{:>16.3f}{:>20.3f}{:>14.3f}                                                                     0    0.0000\n'.format(
                        node,self.nodes[node]['x'],self.nodes[node]['y'],self.nodes[node]['z']))
                
            
            
        
            
