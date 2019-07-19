# -*- coding: utf-8 -*-
"""
Created on Wed Nov 28 11:35:27 2018

@author: smrak
"""

import dascutils as du
from argparse import ArgumentParser
import os

def _convert(folder: str = '',
             azel: list = None,
             wl: int = 558,
             tlim: list = None,
             coordinate: str = 'polar',
             mapping_altitude: int = None,
             el_mask: int = None,
             ofn: str = None):
    if (azel is None) or (None in azel):
        az_cal = os.path.join( os.getcwd(), 'cal/PKR_DASC_0558_20150213_Az.FIT')
        el_cal = os.path.join( os.getcwd(), 'cal/PKR_DASC_0558_20150213_El.FIT')
        azel = [az_cal, el_cal]
    else:
        assert len(azel) == 2
        
    if ofn is None or ofn == '':
        ofn = folder
    
    du.load(fin = folder,
            azelfn = azel,
            treq = tlim,
            wavelenreq = wl, 
            verbose = False,
            coordinate = coordinate,
            mapping_altitude = mapping_altitude,
            el_mask = el_mask,
            ofn = folder)

def main():
    p = ArgumentParser()
    p.add_argument('folder', help='Input folder with FITS files')
    p.add_argument('-o', '--odir', help='directory/filename to write/save the netCDF file')
    p.add_argument('-t', '--tlim', help='start/end times UTC e.g. 2012-11-03T06:23:00', nargs = 2)
    p.add_argument('--azcal', default=None)
    p.add_argument('--elcal', default=None)
    p.add_argument('-c', '--coords', help='coordinate system: polar or wsg', default='polar')
    p.add_argument('-a', '--alt', help='mapping altitude if coord=wsg', default=100, type=int)
    p.add_argument('-w', '--wl', help='Choose the wavelength', default=558)
    p.add_argument('--mask', help='elevation mask', default=None, type=int)
    P = p.parse_args()

    _convert(folder = P.folder, azel=[P.azcal, P.elcal], tlim = P.tlim,
             coordinate = P.coords, mapping_altitude = P.alt, 
             el_mask = P.mask, ofn = P.odir)


if __name__ == '__main__':
    main()