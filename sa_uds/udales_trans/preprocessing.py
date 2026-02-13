import os
import re
import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.optimize import fsolve
import netCDF4 as nc


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
            dapath = os.path.join(simulation_path, str(expnr))
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
             
                            lhs = re.sub(WHITE, VOID, toks[0])
                            rhs = re.sub(WHITE, VOID, toks[1])
    
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
        self.addvar('ltrees', 0)      # switch for trees
        self.addvar('ltreesfile', 0)  # switch for using blocks from a file

        if self.ltrees and not self.ltreesfile:
            #raise Exception("Trees not currently implemented")
            #  These only work with canyons
            self.addvar('tree_dz', 0)  # height above ground
            self.addvar('tree_dx', 0)  # distance from building
            self.addvar('tree_dy', 0)  # spacing between trees
            self.addvar('tree_h', 0)   # tree height (z)
            self.addvar('tree_w', 0)   # tree width (x)
            self.addvar('tree_b', 0)   # tree breadth (y)
            self.addvar('nrows', 0)    # number of tree rows

            #self.addvar('nt1', 0)
            #self.addvar('md', 0)
            #self.addvar('ww', 0)
            #self.addvar('lw', 0)
            #self.addvar('nt2', 0)

        # Trees from file
        if self.ltrees and self.ltreesfile:
            self.addvar('treesfile', '')  # name of blocks file

        self.addvar('lpurif', 0)  # switch for purifiers (not implemented)
        if self.lpurif:
            raise Exception("Purifiers not currently implemented")
            #if self.lcanyons:
            #    self.addvar('purif_dz', 1)   # purifier starting point from bottom
            #    self.addvar('purif_dx', 3)   # distance from block
            #    self.addvar('purif_h', 3)    # purifier height
            #    self.addvar('purif_w', 0)    # purifier width
            #    self.addvar('purif_dy', 1)   # depth of purifier (in y)
            #    self.addvar('purif_sp', 31)  # spacing between purifiers
            #    self.addvar('purif_i', 1)    # case for purifier (1 = +ve x, 2 = -ve x, 3 = +ve y etc.)
            #    self.addvar('npurif', (self.jtot / (self.npurif_dy + self.purif_sp)))

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

        self.addvar('luoutflowr', 0)  # switch that determines whether u-velocity is corrected to get a fixed outflow rate
        self.addvar('lvoutflowr', 0)  # switch that determines whether v-velocity is corrected to get a fixed outflow rate.
        self.addvar('luvolflowr', 0)  # switch that determines whether u-velocity is corrected to get a fixed volume flow rate.
        self.addvar('lvvolflowr', 0)  # switch that determines whether v-velocity is corrected to get a fixed volume flow rate.

        # &DOMAIN
        self.addvar('itot', 64)  # number of cells in x-direction
        self.addvar('xlen', 64)  # domain size in x-direction
        self.addvar('jtot', 64)  # number of cells in y-direction
        self.addvar('ylen', 64)  # domain size in y-direction
        self.addvar('ktot', 96)  # number of cells in z-direction

        self.addvar('dx', self.xlen / self.itot)
        self.addvar('dy', self.ylen / self.jtot)

        # BCs
        self.addvar('BCxm', 1)
        self.addvar('BCym', 1)

        # &ENERGYBALANCE
        self.addvar('lEB', 0)
        self.addvar('lfacTlyrs', 0)

        # &WALLS
        self.addvar('iwallmom', 3)
        self.addvar('iwalltemp', 1)
        self.addvar('lbottom', 0)
        self.addvar('lwritefac', 0)

        # &PHYSICS
        self.addvar('ltempeq', 0)
        self.addvar('lmoist', 0)
        self.addvar('lchem' , 0)     # switch for chemistry (not implemented)
        self.addvar('lprofforc', 0)  # switch for 1D geostrophic forcing
        self.addvar('lcoriol', 0)    # switch for coriolis forcing
        self.addvar('idriver', 0)    # case for driver simulations | 1 - writes driver files | 2 - reads driver files

        if ((not self.luoutflowr) and (not self.lvoutflowr) and (not self.luvolflowr) and (not self.lvvolflowr)
            and (not self.lprofforc) and (not self.lcoriol) and (self.idriver != 2)):
                self.addvar('ldp', 1)
                print('No forcing switch config. setup and not a driven simulation so initial velocities and/or pressure gradients applied.')
        else:
            self.addvar('ldp', 0)

        if (self.ltempeq == 0) or (self.iwalltemp == 1 and self.iwallmom == 2):
            self.iwallmom = 3

        # &INPS
        self.addvar('zsize', 96)          # domain size in z-direction
        self.addvar('lzstretch', 0)       # switch for stretching z grid
        self.addvar('stl_file', '')
        self.addvar('gen_geom', True)     # generate the geometry from scratch
        self.addvar('geom_path', '')      # if not generating the geometry, the path to the geometry files
        self.addvar('diag_neighbs', True)
        self.addvar('stl_ground', True)   # Does STL include facets at ground

        if self.lzstretch:
            self.addvar('stretchconst', 0.01)
            self.addvar('lstretchexp', 0)
            self.addvar('lstretchexpcheck', 0)
            self.addvar('lstretchtanh', 0)
            self.addvar('lstretch2tanh', 0)
            self.addvar('hlin', 0)
            self.addvar('dzlin', 0)
            self.addvar('dz', self.dzlin)
        else:
            self.addvar('dz', self.zsize / self.ktot)

        if self.lEB:
            self.addvar('maxlen', 10)  # maximum size of facets
        else:
            self.addvar('maxlen', np.inf)

        self.addvar('u0', 0)    # initial u-velocity - also applied as geostrophic term where applicable
        self.addvar('v0', 0)    # initial v-velocity - also applied as geostrophic term where applicable
        self.addvar('tke', 0)
        self.addvar('dpdx', 0)   # dp/dx [Pa/m]
        self.addvar('dpdy', 0)   # dp/dy [Pa/m]
        self.addvar('thl0', 288) # temperature at lowest level
        self.addvar('qt0', 0)    # specific humidity

        self.addvar('nsv', 0)    # number of scalar variables (not implemented)

        if self.nsv > 0:
            self.addvar('sv10', 0)        # first scalar variable initial/ background conc.
            self.addvar('sv20', 0)        # second scalar variable initial/ background conc.
            self.addvar('sv30', 0)        # third scalar variable initial/ background conc.
            self.addvar('sv40', 0)        # fourth scalar variable initial/ background conc.
        	self.addvar('sv50', 0)        # fifth scalar variable initial/ background conc.
        	self.addvar('lscasrc', 0)     # switch for scalar point source
        	self.addvar('lscasrcl', 0)    # switch for scalar line source
        	self.addvar('lscasrcr', 0)    # switch for network of scalar point source
        	self.addvar('xS', -1)         # x-position of scalar point source [m]
        	self.addvar('yS', -1)         # y-position of scalar point source [m]
        	self.addvar('zS', -1)         # z-position of scalar point source [m]
            self.addvar('SSp', -1)        # source strength of scalar point source
        	self.addvar('sigSp', -1)      # standard deviation/spread of scalar point source [g] - per unit time??
        	self.addvar('nscasrc', 0)     # number of scalar point sources
            self.addvar('xSb', -1)        # x-position of scalar line source begining point [m]
            self.addvar('ySb', -1)        # y-position of scalar line source begining point [m]
            self.addvar('zSb', -1)        # z-position of scalar line source begining point [m]
            self.addvar('xSe', -1)        # x-position of scalar line source ending point [m]
            self.addvar('ySe', -1)        # y-position of scalar line source ending point [m]
            self.addvar('zSe', -1)        # z-position of scalar line source ending point [m]
            self.addvar('SSl', -1)        # source strength of scalar line source [g/m] - per unit time??
        	self.addvar('sigSl', -1)      # standard deviation/spread of scalar line source
            self.addvar('nscasrcl', 0)    # number of scalar point sources

        self.addvar('lapse', 0)  # lapse rate [K/s]
        self.addvar('w_s', 0)    # subsidence [*units?*]
        self.addvar('R', 0)      # radiative forcing [*units?*]

        self.addvar('libm', 1)

        self.addvar('isolid_bound', 1)
        # Option for solid/fluid detection and boundary points calculation;
        # 1: inmypoly_fortran (Fortran), 2: inmypoly (MATLAB) (useful for debugging),
        # 3: inpolyhedron (MATLAB): https://www.mathworks.com/matlabcentral/fileexchange/37856-inpolyhedron-are-points-inside-a-triangulated-volume

        self.addvar('ifacsec', 1)
        # Option for facet section calculation (matchFacetsToCells)
        # 1: Fortran, 2: MATLAB (useful for debugging)

        self.addvar('read_types', 0)
        if self.read_types:
            self.addvar('types_path', 0)

        if self.lEB:
            self.addvar('xazimuth', 90)  # azimuth of x-direction wrt N. Default: x = East
                                         # north -> xazimuth = 0
                                         # east  -> xazimuth = 90
                                         # south -> xazimuth = 180
                                         # west  -> xazimuth = 270
            self.addvar('ltimedepsw', 0)
            self.addvar('ishortwave', 1)
            # Option for direct shortwave radiation calculation
            # 1: Fortran, 2: MATLAB (useful for debugging)
            self.addvar('isolar', 1)
            # 1: custom (uDALES v1), 2: from lat/long, 3: from weatherfile
            self.addvar('runtime', 0)
            self.addvar('dtEB', 10.0)       # energy balance timestep
            self.addvar('dtSP', self.dtEB)  # solar position time step

            if self.isolar == 1:
                self.addvar('solarazimuth', 135)    # solar azimuth angle
                self.addvar('solarzenith', 28.4066) # zenith angle
                self.addvar('I', 800)               # Direct normal irradiance [W/m2]
                self.addvar('Dsky', 418.8041)       # Diffuse incoming radiation [W/m2]
            elif self.isolar == 2:
                self.addvar('longitude', -0.13) # longitude
                self.addvar('latitude', 51.5)   # latitude
                self.addvar('timezone', 0)      # timezone
                self.addvar('elevation', 0)     # timezone
                self.addvar('hour', 6)
                self.addvar('minute', 0)
                self.addvar('second', 0)
                self.addvar('year', 2011)
                self.addvar('month', 9)
                self.addvar('day', 30)
            elif self.isolar == 3:
                self.addvar('weatherfname', '')
                self.addvar('hour', 0)
                self.addvar('minute', 0)
                self.addvar('second', 0)
                self.addvar('year', 0)
                self.addvar('month', 6)
                self.addvar('day', 1)

            self.addvar('psc_res', 0.1)      # Poly scan conversion resolution for solar radiation calculation (lower number = better)
            self.addvar('lvfsparse', False)  # view factors given in sparse format

            # view3d output format. 0: text, 1: binary, 2: sparse
            self.addvar('calc_vf', True)
            self.addvar('maxD', np.inf)  # maximum distance to check view factors

            if not self.calc_vf:
               self.addvar('vf_path', '')

            self.addvar('view3d_out', 0)
            if (self.view3d_out == 2) and (not self.lvfsparse):
                raise Exception('If sparse view3d output is desired, set lvfsparse=.true. in &ENERGYBALANCE.')

        self.addvar('facT', 288.0)   # Initial facet temperatures.
        self.addvar('nfaclyrs', 3)  # Number of facet layers
        self.addvar('nfcts', 0)
        self.generate_factypes()
        self.addvar('facT_file', '')

    def generate_factypes(self):
        K = self.nfaclyrs
        factypes = []

        # Bounding walls (bw)
        id_bw  = -101
        lGR_bw = 0
        z0_bw  = 0
        z0h_bw = 0
        al_bw  = 0.5
        em_bw  = 0.85
        D_bw   = 0.0
        d_bw   = D_bw / K
        C_bw   = 0.0
        l_bw   = 0.0
        k_bw   = 0.0
        bw = [id_bw, lGR_bw, z0_bw, z0h_bw, al_bw, em_bw] + \
             [d_bw] * K + \
             [C_bw] * K + \
             [l_bw] * K + \
             [k_bw] * (K + 1)
        factypes.append(bw)

        # Floors (f)
        id_f  = -1
        lGR_f = 0
        z0_f  = 0.05
        z0h_f = 0.00035
        al_f  = 0.5
        em_f  = 0.85
        D_f   = 0.5
        d_f   = D_f / K
        C_f   = 1.875e6
        l_f   = 0.75
        k_f   = 0.4e-6

        if (K == 3):
            # Reproduce the original factypes.inp (d_f not constant for each layer)
            f = [id_f, lGR_f, z0_f, z0h_f, al_f, em_f, 0.1, 0.2, 0.2] + \
                [C_f] * K + \
                [l_f] * K + \
                [k_f] * (K + 1)
        else:
            f = [id_f, lGR_f, z0_f, z0h_f, al_f, em_f] + \
                [d_f] * K + \
                [C_f] * K + \
                [l_f] * K + \
                [k_f] * (K + 1)

        factypes.append(f)

        # Dummy (dm)
        id_dm  = 0
        lGR_dm = 0
        z0_dm  = 0
        z0h_dm = 0
        al_dm  = 0
        em_dm  = 0
        D_dm   = 0.3
        d_dm = D_dm / K
        C_dm = 1.875e6
        l_dm = 0.75
        k_dm = 0.4e-6
        dm = [id_dm, lGR_dm, z0_dm, z0h_dm, al_dm, em_dm] + \
             [d_dm] * K + \
             [C_dm] * K + \
             [l_dm] * K + \
             [k_dm] * (K + 1)
        factypes.append(dm)

        # Concrete (c)
        id_c  = 1
        lGR_c = 0
        z0_c  = 0.05
        z0h_c = 0.00035
        al_c = 0.5
        em_c = 0.85
        D_c = 0.36
        d_c = D_c / K
        C_c = 2.5e6
        l_c = 1
        k_c = 0.4e-6
        c = [id_c, lGR_c, z0_c, z0h_c, al_c, em_c] + \
            [d_c] * K + \
            [C_c] * K + \
            [l_c] * K + \
            [k_c] * (K + 1)
        factypes.append(c)

        # Brick (b)
        id_b  = 2
        lGR_b = 0
        z0_b  = 0.05
        z0h_b = 0.00035
        al_b = 0.5
        em_b = 0.85
        D_b = 0.36
        d_b = D_b / K
        C_b = 2.766667e6
        l_b = 0.83
        k_b = 0.3e-6
        b = [id_b, lGR_b, z0_b, z0h_b, al_b, em_b] + \
            [d_b] * K + \
            [C_b] * K + \
            [l_b] * K + \
            [k_b] * (K + 1)
        factypes.append(b)

        # Stone (s)
        id_s  = 3
        lGR_s = 0
        z0_s  = 0.05
        z0h_s = 0.00035
        al_s = 0.5
        em_s = 0.85
        D_s = 0.36
        d_s = D_s / K
        C_s = 2.19e6
        l_s = 2.19
        k_s = 1e-6
        s = [id_s, lGR_s, z0_s, z0h_s, al_s, em_s] + \
            [d_s] * K + \
            [C_s] * K + \
            [l_s] * K + \
            [k_s] * (K + 1)
        factypes.append(s)

        # Wood (w)
        id_w  = 4
        lGR_w = 0
        z0_w  = 0.05
        z0h_w = 0.00035
        al_w = 0.5
        em_w = 0.85
        D_w = 0.36
        d_w = D_w / K
        C_w = 1e6
        l_w = 0.1
        k_w = 0.1e-6
        w = [id_w, lGR_w, z0_w, z0h_w, al_w, em_w] + \
            [d_w] * K + \
            [C_w] * K + \
            [l_w] * K + \
            [k_w] * (K + 1)
        factypes.append(w)

        # GR1
        id_GR1 = 11
        lGR_GR1 = 1
        z0_GR1 = 0.05
        z0h_GR1 = 0.00035
        al_GR1 = 0.25
        em_GR1 = 0.95
        D_GR1 = 0.6
        d_GR1 = D_GR1 / K
        C_GR1 = 5e6
        l_GR1 = 2
        k_GR1 = 0.4e-6
        GR1 = [id_GR1, lGR_GR1, z0_GR1, z0h_GR1, al_GR1, em_GR1] + \
              [d_GR1] * K + \
              [C_GR1] * K + \
              [l_GR1] * K + \
              [k_GR1] * (K + 1)
        factypes.append(GR1)

        # GR2
        id_GR2 = 12
        lGR_GR2 = 1
        z0_GR2 = 0.05
        z0h_GR2 = 0.00035
        al_GR2 = 0.35
        em_GR2 = 0.90
        D_GR2 = 0.6
        d_GR2 = D_GR2 / K
        C_GR2 = 2e6
        l_GR2 = 0.8
        k_GR2 = 0.4e-6
        GR2 = [id_GR2, lGR_GR2, z0_GR2, z0h_GR2, al_GR2, em_GR2] + \
              [d_GR2] * K + \
              [C_GR2] * K + \
              [l_GR2] * K + \
              [k_GR2] * (K + 1)
        factypes.append(GR2)

        self.addvar('factypes', np.array(factypes))

    def write_facets(self, types, normals):
        fname = f'facet.inp.{self.expnr}'

        with open(fname, 'w') as fileID:
            fileID.write('# type, normal\n')

            if types.ndim == 1:
                types = types.reshape(-1, 1)

            if normals.ndim == 1:
                normals = normals.reshape(1, -1)

            data = np.hstack([types, normals])

            for row in data:
                fileID.write(f'{row[0]:<4.0f} {row[1]:<4.4f} {row[2]:<4.4f} {row[3]:<4.4f}\n')

    def write_factypes(self):
        K = self.nfaclyrs

        fname = f'factypes.inp.{self.expnr}'

        dheaderstring = ''
        for k in range(1, K + 1):
            dheaderstring += f'  d{k} [m]'

        Cheaderstring = ''
        for k in range(1, K + 1):
            Cheaderstring += f'  C{k} [J/(K m^3)]'

        lheaderstring = ''
        for k in range(1, K + 1):
            lheaderstring += f'  l{k} [W/(m K)]'

        kheaderstring = ''
        for k in range(1, K + 2):
            kheaderstring += f'  k{k} [W/(m K)]'

        with open(fname, 'w') as fileID:
            fileID.write(f'# walltype, {K} layers per type where layer 1 is the outdoor side and layer {K} is indoor side\n')
            fileID.write('# 0=default dummy, -1=asphalt floors; -101=concrete bounding walls; 1=concrete; 2=bricks; 3=stone; 4=painted wood; 11=GR1; 12=GR2\n')
            fileID.write(f'# wallid  lGR  z0 [m]  z0h [m]  al [-]  em [-]{dheaderstring}{Cheaderstring}{lheaderstring}{kheaderstring}\n')

            valstring1 = '{:8d}  {:3d}  {:6.2f}  {:7.5f}  {:6.2f}  {:6.2f}'

            valstring2 = ''
            for k in range(1, K + 1):
                valstring2 += '  {:6.2f}'

            for k in range(1, K + 1):
                valstring2 += '  {:14.0f}'

            for k in range(1, K + 1):
                valstring2 += ' {:13.4f}'

            for k in range(1, K + 2):
                valstring2 += ' {:13.8f}'

            valstring = f'{valstring1}{valstring2}'

            nfactypes = self.factypes.shape[0]

            for i in range(nfactypes):
                row_data = self.factypes[i, :]
                fileID.write(valstring.format(*row_data) + '\n')

    def plot_profiles(self):
        plt.figure(figsize=(16, 4))

        plt.subplot(1, 4, 1)
        plt.plot(self.pr[:, 1], np.arange(1, self.ktot + 1))
        plt.title('Temperature')

        plt.subplot(1, 4, 2)
        plt.plot(self.ls[:, 9], np.arange(1, self.ktot + 1))
        plt.title('Radiative forcing')

        plt.subplot(1, 4, 3)
        plt.plot(self.ls[:, 5], np.arange(1, self.ktot + 1))
        plt.title('Subsidence')

        plt.subplot(1, 4, 4)
        plt.plot(self.ls[:, 1], np.arange(1, self.ktot + 1), label='u')
        plt.plot(self.ls[:, 2], np.arange(1, self.ktot + 1), linestyle='--', color='red', label='v')
        plt.title('Velocity')
        plt.legend()

        plt.tight_layout()
        plt.show()

    def generate_xygrid(self):
        self.addvar('xf', np.arange(0.5 * self.dx, self.xlen, self.dx))
        self.addvar('yf', np.arange(0.5 * self.dy, self.ylen, self.dy))
        self.addvar('xh', np.arange(0, self.xlen + self.dx, self.dx))
        self.addvar('yh', np.arange(0, self.ylen + self.dy, self.dy))

    def write_xgrid(self):
        fname = f'xgrid.inp.{self.expnr}'

        with open(fname, 'w') as xgrid:
            xgrid.write(f'{"#     x-grid":>12}\n')
            xgrid.write(f'{"#           ":>12}\n')

            for x in self.xf:
                xgrid.write(f'{x:<20.15f}\n')

    def generate_zgrid(self):
        if not self.lzstretch:
            self.addvar('zf', np.arange(0.5 * self.dz, self.zsize, self.dz))
            self.addvar('zh', np.arange(0, self.zsize + self.dz, self.dz))
            self.addvar('dzf', (self.zh[1:] - self.zh[:-1]))
        else:
            if self.lstretchexp:
                self.stretch_exp()
            elif self.lstretchexpcheck:
                self.stretch_exp_check()
            elif self.lstretchtanh:
                self.stretch_tanh()
            elif self.lstretch2tanh:
                self.stretch_2tanh()
            else:
                raise Exception('Invalid stretch')

            plt.ioff()

            fig, ax = plt.subplots()
            ax.plot(self.dzf)
            ax.set_title('dz variation')
            ax.set_xlabel(r'$k$')
            ax.set_ylabel(r'$dz$')
            ax.axis('tight')

            plt.savefig('dz_variation.png')
            plt.close(fig)

            plt.ion()

    def stretch_exp(self):
        il = int(round(self.hlin / self.dzlin))
        ir = self.ktot - il

        self.addvar('zf', np.zeros(self.ktot))
        self.addvar('dzf', np.zeros(self.ktot))
        self.addvar('zh', np.zeros(self.ktot + 1))

        self.zf[:il] = np.arange(0.5 * self.dzlin, self.hlin + 0.5 * self.dzlin, self.dzlin)
        self.zh[:il + 1] = np.arange(0, self.hlin + self.dzlin, self.dzlin)

        gf = self.stretchconst

        while True:
            indices = np.arange(0, ir + 1, 1)
            self.zh[il:] = self.zh[il] + (self.zsize - self.zh[il]) * (np.exp(gf * indices / ir) - 1) / (np.exp(gf) - 1)  # dh has been replaced by zsize

            if (self.zh[il + 1] - self.zh[il]) < self.dzlin:
                gf -= 0.01  # make sufficiently small steps to avoid an initial bump in dz
            else:
                if (self.zh[-1] - self.zh[-2]) > 3 * self.dzlin:
                    print('Warnning: final grid spacing large - consider reducing domain height')
                break

        self.zf = (self.zh[:-1] + self.zh[1:]) / 2
        self.dzf = self.zh[1:] - self.zh[:-1]

    def stretch_exp_check(self):
        il = int(round(self.hlin / self.dzlin))
        ir = self.ktot - il
        z0 = il * self.dzlin  # hlin will be modified as z0

        self.addvar('zf', np.zeros(self.ktot))
        self.addvar('dzf', np.zeros(self.ktot))
        self.addvar('zh', np.zeros(self.ktot + 1))

        # Introduce zhat(xi) = (z(xi)-z0) / L where xi = [0, 1] is the
        # computational space variable which is discretised uniformly. Note that
        # zhat = [0, 1] also by construction.
        #
        # Use a function zhat = A (exp(alpha xi)-1) to represent the
        # grid-nonuniformity. There are three conditions on this function:
        #
        #   zhat(0) = 0,       zhat(1) = 1.
        #
        #   dz/dxi(0) = dz/dzhat dzhat/dxi = L dzhat/dxi <= dz0*N
        #
        # Solving this for the function above results in
        #
        # A = 1 / (exp(alpha)-1) and
        #
        # alpha / (exp(alpha)-1) = (dz0*N)/L
        #
        # The last equation will need to be determined via a root finding procedure.

        L = self.zsize - z0
        dxi = 1 / ir
        xi = np.linspace(0, 1, ir + 1)

        # determine alpha; alpha is exponential stretch constant
        def eq(alpha):
            return alpha - (self.dzlin * ir) / L * (np.exp(alpha) - 1)

        alpha_sol = fsolve(eq, 1.0)
        alpha = alpha_sol[0]
        A = 1 / (np.exp(alpha) - 1.0)
        # print(f'alpha value chosen: alpha = {alpha:8.4f}\n')

        zhat = lambda xi_val: A * (np.exp(alpha * xi_val) - 1.0)
        z_func = lambda xi_val: z0 + zhat(xi_val) * L

        # create grid
        self.zh[0:il+1] = np.arange(0, z0 + self.dzlin/2, self.dzlin)  # linear part
        self.zh[il:self.ktot + 1] = z_func(xi)  # stretched part

        # perform grid quality checks
        dz = np.diff(self.zh)
        stretch = dz[1:] / dz[:-1]
        if (np.min(stretch) < 0.95) or (np.max(stretch) > 1.05):
            print('WARNING -- generated grid is of bad quality')
            print('Stretching factor = dz(n+1)/dz(n) should be between 0.95 and 1.05')
            print(f'min value = {np.min(stretch):8.3f}')
            print(f'max value = {np.max(stretch):8.3f}')

        # give a warning if the grid is refined near the top
        if alpha < 0:
            print('WARNING -- possibly incorrect value for alpha')
            print('The calculated value of alpha is less than zero, which implies you are refining the grid towards the domain top.')

        self.zf = (self.zh[1:] + self.zh[:-1]) / 2.0
        self.dzf = self.zh[1:] - self.zh[:-1]
    
    def stretch_tanh(self):
        il = int(round(self.hlin / self.dzlin))
        ir = self.ktot - il

        self.addvar('zf', np.zeros(self.ktot))
        self.addvar('dzf', np.zeros(self.ktot))
        self.addvar('zh', np.zeros(self.ktot + 1))

        self.zf[:il] = np.arange(0.5 * self.dzlin, self.hlin + 0.5 * self.dzlin, self.dzlin)
        self.zh[:il + 1] = np.arange(0, self.hlin + self.dzlin, self.dzlin)

        gf = self.stretchconst

        while True:
            self.zh[il:] = self.zh[il] + (self.zsize - self.zh[il]) * (1 - np.tanh(gf * (1 - 2 * np.arange(0, ir + 1, 1) / (2 * ir))) / np.tanh(gf)))

            if (self.zh[il + 1] - self.zh[il]) < self.dzlin:
                gf -= 0.01  # make sufficiently small steps to avoid an initial bump in dz
            else:
                if (self.zh[-1] - self.zh[-2]) > 3 * self.dzlin:
                    print('Warning: final grid spacing large - consider reducing domain height')
                    break

            for i in range(self.ktot):
                self.zf[i] = 0.5 * (self.zh[i] + self.zh[i + 1])
                self.dzf[i] = self.zh[i + 1] - self.zh[i]

    def stretch_2tanh(self):
        il = int(round(self.hlin / self.dzlin))
        ir = self.ktot - il

        self.addvar('zf', np.zeros(self.ktot))
        self.addvar('dzf', np.zeros(self.ktot))
        self.addvar('zh', np.zeros(self.ktot + 1))

        self.zf[:il] = np.arange(0.5 * self.dzlin, self.hlin + 0.5 * self.dzlin, self.dzlin)
        self.zh[:il + 1] = np.arange(0, self.hlin + self.dzlin, self.dzlin)

        gf = self.stretchconst

        while True:
            self.zh[il:] = self.zh[il] + (self.zsize - self.zh[il]) / 2 * (1 - np.tanh(gf * (1 - 2 * np.arange(0, ir + 1, 1) / ir)) / np.tanh(gf))

            if (self.zh[il + 1] - self.zh[il]) < self.dzlin:
                gf -= 0.01  # make sufficiently small steps to avoid an initial bump in dz
            else:
                if np.max(np.diff(self.zh)) > 3 * self.dzlin:
                    print('Warning: final grid spacing large - consider reducing domain height')
                    break

        for i in range(self.ktot):
            self.zf[i] = (self.zh[i] + self.zh[i + 1]) / 2
            self.dzf[i] = self.zh[i + 1] - self.zh[i]

    def write_zgrid(self):
        fname = f'zgrid.inp.{self.expnr}'
        with open(fname, 'w') as zgrid:
            zgrid.write(f"{'#     z-grid':12s}\n")
            zgrid.write(f"{'#           ':12s}\n")
            for z in self.zf:
                zgrid.write(f"{z:20.15f}\n")

    def generate_lscale(self):
        if sum([(self.luoutflowr or self.lvoutflowr), (self.luvolflowr or self.lvvolflowr), self.lprofforc, self.lcoriol, self.ldp]) > 1:
            raise Exception("More than one forcing type specified")

        self.addvar('ls', np.zeros((len(self.zf), 10))

        self.ls[:, 0] = self.zf
        self.ls[:, 5] = self.w_s
        self.ls[:, 9] = self.R

        if self.lprofforc or self.lcoriol:
            self.ls[:, 1] = self.u0
            self.ls[:, 2] = self.v0
        elif self.ldp:
            self.ls[:, 3] = self.dpdx
            self.ls[:, 4] = self.dpdy

    def write_lscale(self):
        fname = f'lscale.inp.{self.expnr}'
        with open(fname, 'w') as lscale:
            lscale.write(f"{'# SDBL flow':12s}\n")
            lscale.write(f"{'# z uq vq pqx pqy wfls dqtdxls dqtdyls dqtdtls dthlrad':60s}\n")
            for row in self.ls:
                lscale.write(f"{row[0]:<20.15f} {row[1]:<12.6f} {row[2]:<12.6f} {row[3]:<12.9f} {row[4]:<12.6f} {row[5]:<15.9f} {row[6]:<12.6f} {row[7]:<12.6f} {row[8]:<12.6f} {row[9]:<17.12f}\n")

    def generate_prof(self):
        self.addvar('pr', np.zeros((len(self.zf), 6)))
        self.pr[:, 0] = self.zf

        if self.lapse:
            thl = np.zeros(self.ktot)
            thl[0] = self.thl0
            for k in range(self.ktot - 1):
                thl[k + 1] = thl[k] + self.lapse * self.zsize / self.ktot
            self.pr[:, 1] = thl
        else:
            self.pr[:, 1] = self.thl0

        self.pr[:, 2] = self.qt0
        self.pr[:, 3] = self.u0
        self.pr[:, 4] = self.v0
        self.pr[:, 5] = self.tke

    def write_prof(self):
        fname = f'prof.inp.{self.expnr}'
        with open(fname, 'w') as prof:
            prof.write(f"{'# SDBL flow':<12s}\n")
            prof.write(f"{'# z thl qt u v tke':<60s}\n")
            for row in self.pr:
                prof.write(f"{row[0]:20.15f} {row[1]:12.6f} {row[2]:12.6f} {row[3]:12.6f} {row[4]:12.6f} {row[5]:12.6f}\n")

    def generate_scalar(self):
        self.addvar('sc', np.zeros((len(self.zf), self.nsv + 1)))
        self.sc[:, 0] = self.zf

        if self.nsv > 0:
            self.sc[:, 1] = self.sv10
        if self.nsv > 1:
            self.sc[:, 2] = self.sv20
        if self.nsv > 2:
            self.sc[:, 3] = self.sv30
        if self.nsv > 3:
            self.sc[:, 4] = self.sv40
        if self.nsv > 4:
            self.sc[:, 5] = self.sv50

    def write_scalar(self):
        fname = f'scalar.inp.{self.expnr}'
        with open(fname, 'w') as scalar:
            scalar.write(f"{'# SDBL flow':<12s}\n")
            scalar.write(f"{'# z scaN,  N=1,2...nsv':<60s}\n")
            for row in self.sc:
                line = f"{row[0]:<20.15f}"
                for i in range(1, self.nsv + 1):
                    line += f" {row[i]:<14.10f}"
                scalar.write(line + "\n")

    def generate_scalarsources(self):
        if ((self.lscasrc) and (self.nscasrc < 2) and any([self.nsv == 0, self.nscasrc < 1, self.xS == -1, self.yS == -1, self.zS == -1, self.SSp == -1, self.sigSp == -1])):
            raise Exception("Must set non-zero positive nsv and nscasrc under &SCALARS, and appropriate xS, yS, zS, SSp and sigSp under &INPS for scalar point source")
        if ((self.lscasrcl) and (self.nscasrcl < 2) and any([self.nsv == 0, self.nscasrcl < 1, self.xSb == -1, self.ySb == -1, self.zSb == -1, self.xSe == -1, self.ySe == -1, self.zSe == -1, self.SSl == -1, self.sigSl == -1])):
            raise Exception("Must set non-zero positive nsv and nscasrcl &SCALARS, and appropriate xSb, ySb, zSb, xSe, ySe, zSe, SSl and sigSl under &INPS for scalar line source")
        if self.lascasrcr:
            raise Exception("Network of point sources not currently implemented")

        if self.lscasrc:
            self.addvar('scasrcp', np.zeros((self.nscasrc, 5)))
            if self.nscasrc == 1:
                self.scasrcp[0, 0] = self.xS
                self.scasrcp[0, 1] = self.yS
                self.scasrcp[0, 2] = self.zS
                self.scasrcp[0, 3] = self.SSp
                self.scasrcp[0, 4] = self.sigSp
            if (self.nscasrc > 1 or self.nsv > 1):
                print('Warning!! Manually set appropriate xS, yS, zS, SS and sigS for scalar source points in scalarsourcep.inp.')

        if self.lscasrcl:
            self.addvar('scasrcl', np.zeros((self.nscasrcl, 8)))
            if self.nscasrcl == 1:
                self.scasrcl[0, 0] = self.xSb
                self.scasrcl[0, 1] = self.ySb
                self.scasrcl[0, 2] = self.zSb
                self.scasrcl[0, 3] = self.xSe
                self.scasrcl[0, 4] = self.ySe
                self.scasrcl[0, 5] = self.zSe
                self.scasrcl[0, 6] = self.SSl
                self.scasrcl[0, 7] = self.sigSl
            if self.nscasrcl > 1 or self.nsv > 1:
                print('Warning!! Manually set appropriate xSb, ySb, zSb, xSe, ySe, zSe, SS and sigS for scalar source lines in scalarsourcel.inp.')

    def write_scalarsources(self):
        for ii in range(1, self.nsv + 1):
            if self.lscasrc:
                fname = f'scalarsourcep.inp.{ii}.{self.expnr}'
                with open(fname, 'w') as scasrcp:
                    scasrcp.write(f"{'# Scalar point source data':<30s}\n")
                    scasrcp.write(f"{'#xS yS zS SS sigS':<60s}\n")
                    for row in self.scasrcp:
                        scasrcp.write(f"{row[0]:12.6f}\t {row[1]:12.6f}\t {row[2]:12.6f}\t {row[3]:12.6f}\t {row[4]:12.6f}\t\n")
            if self.lscasrcl:
                fname = f'scalarsourcel.inp.{ii}.{self.expnr}'
                with open(fname, 'w') as self.scasrcl:
                    scasrcl.write(f"{row[0]:12.6f}\t {row[1]:12.6f}\t {row[2]:12.6f}\t {row[3]:12.6f}\t {row[4]:12.6f}\t {row[5]:12.6f}\t {row[6]:12.6f}\t {row[7]:12.6f}\t\n")
            if self.lscasrc or self.lscasrcl:
                print('Ensure scalar source locations do not intersect any building !! If sure, ignore this message.')  # needs to be removed later

    def plot_scalarsources(self):
        for ii in range(1, self.nsv + 1):
            if self.lscasrc:
                fname = f'scalarsourcep.inp.{ii}.{self.expnr}'
                with open(fname, 'r') as fileID:
                    header_line1 = fileID.readline()
                    header_line2 = fileID.readline()

                    data = []
                    for i in range(self.nscasrc):
                        data_line = fileID.readline()
                        values = [float(x) for x in data_line.split() if x]
                        data.append(values)
                data = np.array(data)
                for i in range(self.nscasrc):
                    x, y, z = data[i, 0], data[i, 1], data[i, 2]
                    marker_size = round(15 * data[i, 4])
                    marker_face_color = [0, 0, data[i, 3]/np.max(data[:, 3])]

                    ax.scatter(x, y, z, s=marker_size**2, c=[marker_face_color], marker='o', edgecolors='black')

            if self.lscasrcl:
                fname = f'scalarsourcel.inp.{ii}.{self.expnr}'
                with open(fname, 'r') as fileID:
                    header_line1 = fileID.readline()
                    header_line2 = fileID.readline()

                    data = []
                    for i in range(self.nscasrcl):
                        data_line = fileID.readline()
                        values = [float(x) for x in data_line.split() if x]
                        data.append(values)
                data = np.array(data)
                for i in range(self.nscasrcl):
                    x = [data[i, 0], data[i, 3]]
                    y = [data[i, 1], data[i, 4]]
                    z = [data[i, 2], data[i, 5]]
                    line_width = round(5 * data[i, 7])
                    color = [0, 0, data[i, 6]/np.max(data[:, 6])]

                    ax.plot(x, y, z, linewidth=line_width, color=color)

    def set_nfcts(self, nfcts):
        self.nfcts = nfcts

    def write_vf(self, vf):
        fname = f'vf.nc.inp.{self.expnr}'
        with nc.Dataset(fname, 'w', format='NETCDF4') as ds:
            ds.createDimension('rows', self.nfcts)
            ds.createDimension('columns', self.nfcts)
            varid = ds.createVariable('view factor', 'f4', ('rows', 'columns'))
            varid[:] = vf
            
    def write_vfsparse(self, vfsparse):
        # [i,j,s] = find(vfsparse)
        i, j = np.where(vfsparse >= 5e-7)
        i = i + 1  # add 1 for 1-based indexing (MATLAB compatibility)
        j = j + 1
        s = vfsparse[vfsparse >= 5e-7]

        data = np.column_stack([i, j, s])
        sorted_indices = np.lexsort((data[:, 1], data[:, 0]))
        data = data[sorted_indices]  # sorted by rows

        fname = f'vfsparse.inp.{self.expnr}'
        with open(fname, 'w') as fID:
            for row in data:
                fID.write(f'{int(row[0])} {int(row[1])} {row[2]:.6f}\n')  # write to 6 decimal places

    def write_svf(self, svf):
        fname = f'svf.inp.{self.expnr}'
        with open(fname, 'w') as fileID:
            fileID.write('# sky view factors\n')

        with open(fname, 'a') as fileID:
            np.savetxt(fileID, svf, fmt='%.4f', delimiter=' ')

    def write_facetarea(self, facetarea):
        fname = f'facetarea.inp.{self.expnr}'
        with open(fname, 'w') as fileID:
            fileID.write('# area of facets\n')

        with open(fname, 'a') as fileID:
            np.savetxt(fileID, facetarea, fmt='%.4f', delimiter=' ')

    def write_netsw(self, Knet):
        fname = f'netsw.inp.{self.expnr}'
        with open(fname, 'w') as fileID:
            fileID.write('# net shortwave on facets [W/m2] (including reflections and diffusive)\n')
            np.savetxt(fileID, Knet.flatten(), fmt='%6.4f')

    def write_timedepsw(self, tSP, Knet):
        fname = f'timedepsw.inp.{self.expnr}'
        with open(fname, 'w') as fileID:
            fileID.write('# time-dependent net shortwave on facets [W/m2]. First line: times (1 x nt), then netsw (nfcts x nt)\n')

        with open(fname, 'a') as fileID:
            np.savetxt(fileID, tSP, fmt='%9.2f', delimiter=' ')
            np.savetxt(fileID, Knet, fmt='%9.4f', delimiter=' ')

    def write_Tfacinit(self, Tfacinit):
        fname = f'Tfacinit.inp.{self.expnr}'
        with open(fname, 'w') as fileID:
            fileID.write('# Initial facet tempereatures in radiative equilibrium\n')

        with open(fname, 'a') as fileID:
            np.savetxt(fileID, Tfacinit, fmt='%.4f', delimiter=' ')

    def write_Tfacinit_layers(self, Tfacinit_layers):
        fname = f'Tfacinit_layers.inp.{self.expnr}'
        with open(fname, 'w') as fileID:
            fileID.write('# Initial facet tempereatures in radiative equilibrium\n')

        with open(fname, 'a') as fileID:
            np.savetxt(fileID, Tfacinit_layers, fmt='%.4f', delimiter=' ')

    def write_trees(self):
        fname = f'trees.inp.{self.expnr}'
        with open(fname, 'w') as trees:
            trees.write('# Trees data\n')
            trees.write('# tree_n\t il\t   iu\t   jl\t   ju\t   kl\t   ku\t\n')
            for row in self.trees:
                trees.write(f'{int(row[0]):4d}\t{int(row[1]):4d}\t{int(row[2]):4d}\t{int(row[3]):4d}\t{int(row[4]):4d}\t{int(row[5]):4d}\t\n')

    def generate_trees_from_namoptions(self):
        if not self.ltreesfile:  # self.lcanyons
            tree_dz = self.tree_dz
            tree_dx = self.tree_dx
            tree_dy = self.tree_dy
            tree_h = self.tree_h
            tree_w = self.tree_w
            tree_b = self.tree_b
            nrows = self.nrows
            jtot = self.jtot
            """
            imax = self.imax
            tot = self.jtot
            blockwidth = self.blockwidth
            canyonwidth = self.canyonwidth
            nrows =  imax / (blockwidth + canyonwidth)  # default is /32
            if np.ceil(nrows) != np.floor(nrows):
                l = np.arange(0, 0.5 * imax + 1)
                ind = (np.remainder(0.5 * imax, 1) == 0)
                err = np.vstack([l[ind], (0.5 * imax) / l[ind]])
                print(')
                print('Block system does not fit grid')
                print(f'sum widths to: {err[0, :]}')
                print(f'Current width: {blockwidth + canyonwidth}')
                raise Exception("Incorrect block system")
            if (canyonwidth / (2 * (tree_w + tree_dx))) < 1:
                raise Exception("Trees and spacing won't fit in canyons 2*(tree_dx+tree_w)>canyonwidth")
            elif not self.lcanyons:
                raise Exception("Generate trees is currently implemented specificly for canyons only")
            if (tree_b == 0 or tree_dy == 0):
                ntrees = 2 * nrows
                trees = np.zeros((ntrees, 6))
                trees[0:nrows, 0] = np.arange(0.5 * canyonwidth + blockwidth + tree_dx + 1, imax - 0.5 * canyonwidth + tree_dx + 1 + (canyonwidth + blockwidth), canyonwidth + blockwidth)
                trees[0:nrows, 1] = trees[0:nrows, 0] + tree_w - 1
                trees[nrows:, 0] = np.arange(0.5 * canyonwidth - tree_w - tree_dx + 1, imax - 0.5 * canyonwidth - blockwidth - tree_w - tree_dx + 1 + (canyonwidth + blockwidth), canyonwidth + blockwidth)
                trees[nrows:, 1] = trees[nrows:, 0] + tree_w - 1
                trees[:, 2] = 1
                trees[:, 3] = jtot
                trees[:, 4] = tree_dz + 1
                trees[:, 5] = tree_dz + tree_h - 1
            else:
            """
            ncols = int(np.floor(jtot / (tree_b + tree_dy)))
            ntrees = 2 * nrows * ncols
            tree_i = np.arange(ntrees)
            tree_i = tree_i.reshape((ncols, 2 * nrows), order='F')
            extra_dy = 0.5 * (jtot - ncols * (tree_b + tree_dy))
            trees = np.zeros((ntrees, 6))

            vec1 = np.arange(0.5 * canyonwidth + blockwidth + tree_dx + 1, imax - 0.5 * canyonwidth + tree_dx + 1 + (canyonwidth + blockwidth), canyonwidth + blockwidth)
            xpos1 = np.tile(vec1.reshape(-1, 1), (1, ncols)).T.flatten(order='F')
            idx1 = tree_i[:, :nrows].flatten(order='F')
            trees[idx1, 0] = xpos1
            trees[idx1, 1] = trees[idx1, 0] + tree_w - 1

            vec2 = np.arange(0.5 * canyonwidth - tree_w - tree_dx + 1, imax - 0.5 * canyonwidth - blockwidth - tree_w - tree_dx + 1 + (canyonwidth + blockwidth), canyonwidth + blockwidth)
            xpos2 = np.tile(vec2.reshape(-1, 1), (1, ncols)).T.flatten(order='F')
            idx2 = tree_i[:, nrows:].flatten(order='F')
            trees[idx2, 0] = xpos2
            trees[idx2, 1] = trees[idx2, 0] + tree_w - 1

            vec3 = np.arange(np.floor(extra_dy + 0.5 * tree_dy) + 1, jtot - np.ceil(extra_dy + 0.5 * tree_dy) - tree_b + 1 + (tree_b + tree_dy), tree_b + tree_dy)
            y_coords = np.tile(vec3.reshape(-1, 1), (1, 2 * nrows)).flatten(order='F')
            idx3 = tree_i[:ncols, :].flatten(order='F')
            trees[idx3, 2] = y_coords
            trees[idx3, 3] = trees[idx3, 2] + tree_b - 1

            trees[:, 4] = tree_dz + 1
            trees[:, 5] = tree_dz + tree_h - 1
        elif self.ltreesfile:
            trees = np.loadtxt(self.treesfile, skiprows=2)
            ntrees = trees.shape[0]
        # else:
            # raise Exception("trees will not be generated, use canyons or tree.inp file.")

        self.addvar('ntrees', ntrees)
        self.ntrees = ntrees
        self.addvar('trees', trees)

    def plot_trees(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.set_title('Blocks')
        ax.view_init(elev=30, azim=-37.5)
        """
        if self.lbottom:
            clr = [0.85, 0.85, 0.85]
            vertices = [[self.xh[0],  self.yh[0],  self.zh[0]],
                        [self.xh[0],  self.yh[-1], self.zh[0]],
                        [self.xh[-1], self.yh[-1], self.zh[0]],
                        [self.xh[-1], self.yh[0],  self.zh[0]]]
            ax.add_collection3d(Poly3DCollection([vertices], facecolors=clr, alpha=0.9))

        if not self.lflat and not self.lfloors:
            clr = [0.85, 0.85, 0.85]
            for i in range(self.nblockstotal):
                il = int(self.blocks[i, 0])
                iu = int(self.blocks[i, 1])
                jl = int(self.blocks[i, 2])
                ju = int(self.blocks[i, 3])
                kl = int(self.blocks[i, 4])
                ku = int(self.blocks[i, 5])

                if i < self.nblocks:
                    vertices = [[self.xh[il],   self.yh[jl],   self.zh[ku+1]],
                                [self.xh[iu+1], self.yh[jl],   self.zh[ku+1]],
                                [self.xh[iu+1], self.yh[ju+1], self.zh[ku+1]],
                                [self.xh[il],   self.yh[ju+1], self.zh[ku+1]]]
                    ax.add_collection3d(Poly3DCollection([vertices], facecolors=clr, alpha=0.9))
                    vertices = [[self.xh[il],   self.yh[jl], self.zh[kl]],
                                [self.xh[il],   self.yh[jl], self.zh[ku+1]],
                                [self.xh[iu+1], self.yh[jl], self.zh[ku+1]],
                                [self.xh[iu+1], self.yh[jl], self.zh[kl]]]
                    ax.add_collection3d(Poly3DCollection([vertices], facecolors=clr, alpha=0.9))
                    vertices = [[self.xh[il],   self.yh[ju+1], self.zh[kl]],
                                [self.xh[il],   self.yh[ju+1], self.zh[ku+1]],
                                [self.xh[iu+1], self.yh[ju+1], self.zh[ku+1]],
                                [self.xh[iu+1], self.yh[ju+1], self.zh[kl]]]
                    ax.add_collection3d(Poly3DCollection([vertices], facecolors=clr, alpha=0.9))
                    vertices = [[self.xh[il], self.yh[ju+1], self.zh[kl]],
                                [self.xh[il], self.yh[ju+1], self.zh[ku+1]],
                                [self.xh[il], self.yh[jl],   self.zh[ku+1]],
                                [self.xh[il], self.yh[jl],   self.zh[kl]]]
                    ax.add_collection3d(Poly3DCollection([vertices], facecolors=clr, alpha=0.9))
                    vertices = [[self.xh[iu+1], self.yh[jl],   self.zh[kl]],
                                [self.xh[iu+1], self.yh[jl],   self.zh[ku+1]],
                                [self.xh[iu+1], self.yh[ju+1], self.zh[ku+1]],
                                [self.xh[iu+1], self.yh[ju+1], self.zh[kl]]]
                    ax.add_collection3d(Poly3DCollection([vertices], facecolors=clr, alpha=0.9))
                else:
                    vertices = [[self.xh[il],   self.yh[jl],   self.zh[ku+1]],
                                [self.xh[iu+1], self.yh[jl],   self.zh[ku+1]],
                                [self.xh[iu+1], self.yh[ju+1], self.zh[ku+1]],
                                [self.xh[il],   self.yh[ju+1], self.zh[ku+1]]]
                    ax.add_collection3d(Poly3DCollection([vertices], facecolors=clr, alpha=0.9))
                    vertices = [[self.xh[il],   self.yh[jl], 0],
                                [self.xh[il],   self.yh[jl], self.zh[ku+1]],
                                [self.xh[iu+1], self.yh[jl], self.zh[ku+1]],
                                [self.xh[iu+1], self.yh[jl], 0]]
                    ax.add_collection3d(Poly3DCollection([vertices], facecolors=clr, alpha=0.9))
                    vertices = [[self.xh[il],   self.yh[ju+1], 0],
                                [self.xh[il],   self.yh[ju+1], self.zh[ku+1]],
                                [self.xh[iu+1], self.yh[ju+1], self.zh[ku+1]],
                                [self.xh[iu+1], self.yh[ju+1], 0]]
                    ax.add_collection3d(Poly3DCollection([vertices], facecolors=clr, alpha=0.9))
                    vertices = [[self.xh[il], self.yh[ju+1], 0],
                                [self.xh[il], self.yh[ju+1], self.zh[ku+1]],
                                [self.xh[il], self.yh[jl],   self.zh[ku+1]],
                                [self.xh[il], self.yh[jl],   0]]
                    ax.add_collection3d(Poly3DCollection([vertices], facecolors=clr, alpha=0.9))
                    vertices = [[self.xh[iu+1], self.yh[jl],   0],
                                [self.xh[iu+1], self.yh[jl],   self.zh[ku+1]],
                                [self.xh[iu+1], self.yh[ju+1], self.zh[ku+1]],
                                [self.xh[iu+1], self.yh[ju+1], 0]]
                    ax.add_collection3d(Poly3DCollection([vertices], facecolors=clr, alpha=0.9))
        """
        if self.ltrees:
            clr = [0.20, 0.65, 0.15]
            for i in range(self.ntrees):
                il = int(self.trees[i, 0])
                iu = int(self.trees[i, 1])
                jl = int(self.trees[i, 2])
                ju = int(self.trees[i, 3])
                kl = int(self.trees[i, 4])
                ku = int(self.trees[i, 5])
                vertices = [[self.xh[il],   self.yh[jl],   self.zh[ku+1]],
                            [self.xh[iu+1], self.yh[jl],   self.zh[ku+1]],
                            [self.xh[iu+1], self.yh[ju+1], self.zh[ku+1]],
                            [self.xh[il],   self.yh[ju+1], self.zh[ku+1]]]
                ax.add_collection3d(Poly3DCollection([vertices], facecolors=clr, alpha=0.9))
                vertices = [[self.xh[il],   self.yh[jl], self.zh[kl]],
                            [self.xh[il],   self.yh[jl], self.zh[ku+1]],
                            [self.xh[iu+1], self.yh[jl], self.zh[ku+1]],
                            [self.xh[iu+1], self.yh[jl], self.zh[kl]]]
                ax.add_collection3d(Poly3DCollection([vertices], facecolors=clr, alpha=0.9))
                vertices = [[self.xh[il],   self.yh[ju+1], self.zh[kl]],
                            [self.xh[il],   self.yh[ju+1], self.zh[ku+1]],
                            [self.xh[iu+1], self.yh[ju+1], self.zh[ku+1]],
                            [self.xh[iu+1], self.yh[ju+1], self.zh[kl]]]
                ax.add_collection3d(Poly3DCollection([vertices], facecolors=clr, alpha=0.9))
                vertices = [[self.xh[il], self.yh[ju+1], self.zh[kl]],
                            [self.xh[il], self.yh[ju+1], self.zh[ku+1]],
                            [self.xh[il], self.yh[jl],   self.zh[ku+1]],
                            [self.xh[il], self.yh[jl],   self.zh[kl]]]
                ax.add_collection3d(Poly3DCollection([vertices], facecolors=clr, alpha=0.9))
                vertices = [[self.xh[iu+1], self.yh[jl],   self.zh[kl]],
                            [self.xh[iu+1], self.yh[jl],   self.zh[ku+1]],
                            [self.xh[iu+1], self.yh[ju+1], self.zh[ku+1]],
                            [self.xh[iu+1], self.yh[ju+1], self.zh[kl]]]
                ax.add_collection3d(Poly3DCollection([vertices], facecolors=clr, alpha=0.9))

        #ax.set_xlim([0, self.xh[-1]])
        #ax.set_ylim([0, self.yh[-1]])
        #ax.set_zlim([0, self.zh[-1]])
        #ax.set_xlabel('$x(\\mathrm{m})$')
        #ax.set_ylabel('$y(\\mathrm{m})$')
        #ax.set_zlabel('$z(\\mathrm{m})$')
        #ax.set_box_aspect([1, 1, 1])
        #ax.grid(True)

        plt.show()

    def update_namoptions(self, namoptionsfile, sectionname, varname, value):
        with open(namoptionsfile, 'r') as f:
            namoptions_content = f.read()

        pattern = varname + r'\s*=\s*\d+'

        if re.search(r'\b' + varname + r'\b', namoptions_content):
            new_content = re.sub(pattern, f'{varname} = {value}', namoptions_content)
        elif sectionname in namoptions_content:
            replacement = f'{sectionname}\n{varname} = {value}'
            new_content = namoptions_content.replace(sectionname, replacement, 1)
        else:
            namoptions_content = namoptions_content + f'\n{sectionname}'
            replacement = f'{sectionname}\n{varname} = {value}'
            new_content = namoptions_content.replace(sectionname, replacement, 1)
            new_content = new_content + '\n/'

        with open(namoptionsfile, 'w') as f:
            f.write(new_content)

    @staticmethod
    def _loadvar(filename, svar):
        """
        Load netcdf data

        Arg:
            filename: Name of file (string)
            svar: Variable name (string)
        Return:
            data: Array of float
        """
        data = None
        with nc.Dataset(filename, 'r') as dataset:
            if svar in dataset.variables:
                data = dataset.variables[svar][:]
                found = True
            else:
                found = False

        if not found:
            print(f'variable {svar} not found!')

        return data
