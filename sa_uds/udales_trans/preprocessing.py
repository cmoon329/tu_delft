import os
import re
import math
import numpy as np

class Preprocessing:
    """Class for pre-processing in uDALES"""

    def __init__(self, expnr=None, simulation_path=None):
        """ 
        /preprocessing.m -> line 21~98 
        
        <Class constructor>
    
        Arg:
            expnr: Integer equal to simulation number
            simulation_path: path to simulations 
        """
        TOKENS = r'(.*)\=(.*)'
        DROP = r'(\s*|\[|\]|''|''|;)'
        WHITE = r'\s*'
        VOID = ''
        
        self._cpath = os.getcwd()
    
        if expnr is None and simulation_path is None:
            print(f"expnr input not fountd. Exiting...")
        elif expnr is not None and simulation_path is not None:
            dapath = "".join(simulation_path, str(expnr))
        else:
            dapath = str(expnr)
    
        os.chdir(dapath)
        self._path = os.getcwd()
    
        expstr = f"{expnr:03d}"
        filename = f"namoptions.{expstr}"
        try:
            with open(filename, 'r') as fid:
                self._expnr = expstr
    
                for line in fid:
                    if line.strip():
                        match = re.search(TOKENS, line)
                    
                        if match:
                            toks = match.groups()
             
                            lhs = re.sub(WHITE, VOID, toks.group(1))
                            rhs = re.sub(WHITE, VOID, toks.group(2))
    
                            if rhs == '.false.':
                                lhs_value = 0
                            elif rhs == '.true.':
                                lhs_value = 1
                            elif rhs.isdigit():  # check if it is a number
                                lhs_value = float(rhs)
                            else:
                                try:
                                    lhs_value = float(rhs)
                                except:
                                    lhs_value = rhs
                                    
                            setattr(self, lhs, lhs_value)
        except: 
            print(f"{filename} not found. Exiting...")
    
        os.chdir(self._cpath)

    def addvar(self, lhs, var):
        """
        /preprocessing.m -> line 100~111
        
        Function that installs a variable.
    
        Input:
            lhs: Identifier for variable
            var: R-value (value of variable)
        """
        if not hasattr(self, lhs):
            setattr(self, lhs, var)

    def gopath(self):
        """
        /preprocessing.m -> line 115~120
        
        Function that goes to simulation path.
        """
        os.chdir(self._path)

    def gohome(self):
        """
        /preprocessing.m -> line 122~127
        
        Function that goes to work path.
        """
        os.chdir(self._cpath)

    def chcpath(self, newpath):
        """
        /preprocessing.m -> line 122~127
        
        Function that changes work path

        Input:
            newpath: new cpath
        """
        here = os.getcwd()
        os.chdir(newpath)
        self._cpath = os.getcwd()
        os.chdir(here)

    def set_defaults(self):
        """
        /preprocessing.m -> line 122~127
        
        Function that changes work path

        Input:
            newpath: new cpath
        """
        self.addvar(self, 'ltrees', 0)      # switch for trees
        self.addvar(self, 'ltreesfile', 0)  # switch for using blocks from a file

        if self.ltrees and not self.ltreesfile:
            #raise Exception("Trees not currently implemented")
            #  These only work with canyons
            self.addvar(self, 'tree_dz', 0)  # height above ground
            self.addvar(self, 'tree_dx', 0)  # distance from building
            self.addvar(self, 'tree_dy', 0)  # spacing between trees
            self.addvar(self, 'tree_h', 0)   # tree height (z)
            self.addvar(self, 'tree_w', 0)   # tree width (x)
            self.addvar(self, 'tree_b', 0)   # tree breadth (y)
            self.addvar(self, 'nrows', 0)    # number of tree rows

            #self.addvar(self, 'nt1', 0)
            #self.addvar(self, 'md', 0)
            #self.addvar(self, 'ww', 0)
            #self.addvar(self, 'lw', 0)
            #self.addvar(self, 'nt2', 0)

        # Trees from file 
        if self.ltrees and self.ltreesfile:
            self.addvar(self, 'treesfile', '')  # name of blocks file


        self.addvar(self, 'lpurif', 0)  # switch for purifiers (not implemented)
        if self.lpurif:
            raise Exception("Purifiers not currently implemented")
            #if self.lcanyons:
            #    self.addvar(self, 'purif_dz', 1)   # purifier starting point from bottom
            #    self.addvar(self, 'purif_dx', 3)   # distance from block
            #    self.addvar(self, 'purif_h', 3)    # purifier height
            #    self.addvar(self, 'purif_w', 0)    # purifier width
            #    self.addvar(self, 'purif_dy', 1)   # depth of purifier (in y)
            #    self.addvar(self, 'purif_sp', 31)  # spacing between purifiers
            #    self.addvar(self, 'purif_i', 1)    # case for purifier (1 = +ve x, 2 = -ve x, 3 = +ve y etc.)
            #    self.addvar(self, 'npurif', (self.jtot / (self.npurif_dy + self.purif_sp)))

            #    if math.ceil(self.npurif) != math.floor(self.npurif):
            #        lp = np.arange(0, (self.tot/2 + 1))
            #        indp = np.mod(self.jtot/2, lp) == 0
            #        errp = np.vstack([lp[indp], (self.jtot/2)/lp[indp]])
            #        print("Purifier layout does not fit grid")
            #        print(f"sum widths to: {str(errp[0])}")
            #        print(f"Current width: {str(self.purif_dy + self.purif_sp)}")
            #        raise Exception("Incorrect purifier layout")
            #else:
            #    raise Exception("Must use lcanyons configuration to use purifiers")

                
        line 213!! 
