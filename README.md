[![image](https://zenodo.org/badge/51016067.svg)](https://zenodo.org/badge/latestdoi/51016067)
[![image](http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat)](http://www.astropy.org/)
[![image](https://travis-ci.org/scivision/dascutils.svg?branch=master)](https://travis-ci.org/scivision/dascutils)
[![image](https://coveralls.io/repos/github/scivision/dascutils/badge.svg?branch=master)](https://coveralls.io/github/scivision/dascutils?branch=master)
[![image](https://ci.appveyor.com/api/projects/status/xrtb6fc3d4ojp507?svg=true)](https://ci.appveyor.com/project/scivision/dascutils)
[![Maintainability](https://api.codeclimate.com/v1/badges/36b08deedc7d2bf750c8/maintainability)](https://codeclimate.com/github/aldebaran1/dascutils/maintainability)

# DASC all-sky camera utilitiess

Utilities for plotting, saving, analyzing the Poker Flat Research Range Digital All Sky Camera. (Other locations, too).

This program handles the corrupted FITS files due to the RAID array failure on 2013 data.

The raw data FITS are one image per file.


## Install

```sh
pip install -e .
```

## Usage
Many analysts may use the API directly, like:
```python
import dascutils as du

data = du.load('tests/PKR_DASC_0558_20151007_082351.743.FITS')
```
This returns an [xarray.Dataset](http://xarray.pydata.org/en/stable/generated/xarray.Dataset.html), which is like a "smart" Numpy array.
The images are index by wavelength if it was specified in the data file, or 'unknown' otherwise.
The images are in a 3-D stack: (time, x, y).
`data.time` is the time of each image.
also several metadata parameters are included like the location of the camera.

### Download raw DASC files by time

Example download October 7, 2015 from 8:23 to 8:54 UTC:

```sh
DownloadDASC 2015-10-07T08:23 2015-10-07T08:54
```

* `-o` download directory 
* `-c` overwrite existing files 
* `-s` three-letter site acronym e.g. `PKR` for poker flat etc.
* `-w` `--wl` camera wavelength [000, 427, 558, 630], default 558

additional options include:

* `-t` specifiy time limits e.g.  `-t 2014-01-02T02:30 2014-01-02T02:35`
* `-w` choose only certain wavelength(s)

### Spatial registration (plate scale)

The `cal/` directory contains `AZ` and `EL` files corresponding to each pixel. 

```python
import dascutils as du

data = dio.load('tests/PKR_DASC_0558_20151007_082351.743.FITS', azelfn='cal/PKR_DASC_20110112')
```

now `data` includes data variables `az` and `el`, same shape as the image(s), along with camera position in `lat0` `lon0` `alt0`.

* Be sure you know if you're using magnetic north or geographic north, or you'll see a rotation by the declination.
* Note the date in the filename--perhaps the camera was moved since before or long after that date?

### Camera Coordinate Transform

Raw all-sky camera images are in all-sky (fish-eye lense) polar coordinates. A conversion into WSG84:lat,lon,alt is available
with `coordinate` and `mapping altitude` options.

```python
import dascutils as du
data = du.load('/path/to/fits/data/', aselfn = '/path/to/cal/files', coordinate = 'wsg', mapping_altitude = 110)
```
It returns an xarray.Dataset with new `lat`, `lon` coordinates and `image` variable with (N, res, res) dimensions (N = number of images,
res = camera resolution)

Coordinate transform returns coordinates in `lon`, `lat` with ascending order and uniform spacing. Transfomr utilizes a super speed-up 
intepolation, making Delauny trainagulation and weights calusulation only once. It takes ~20 seconds to intepolate 1000 images with 512*512
resolution

```python
from dascutils import interpSpeedUp
X = old 2D coordinate array
Y = old 2D coordinate array
img = an image (X.sahpe[0], Y.shape[0]) or a set of images (N, X.sahpe[0], Y.shape[0]), say, N is a time coordinate
X_new, Y_new, Image_interp = interpSpeedUp(x_in = X, y_in = Y, image = img, verbose = False)
```

Get wights only and interpolate using the waights
```python
from dascutils import interpWeights, interp
vtx, wts = interpWeights(x, y, image, N)
interp_image = interp(img, wtx, wts).reshape(N, N)
```

### Convert Raw data to netCDF4

```sh
python dasc2nc.py folder folder -o -c -a -w --tlim --mask
```
* `folder` Input folder with FITS files
* `-o`, `--odir` directory/filename to write/save the netCDF file
* `-t`, `--tlim` start/end times UTC e.g. 2012-11-03T06:23:00', nargs = 2
* `--azcal`
* `--elcal` path to calibration files
* `-c`, `--coords` coordinate system: polar or wsg', default = 'polar'
* `-a`, `--alt` mapping altitude if coord=wsg', default = 100
* `-w`, `--wl` Choose the wavelength', default = 558
* `--mask`, elevation mask', type = int

### Retreiver Pixel brightness as a function of time
Works for stationary `(X, Y)` and moving `(X(t), Y(t))` for givent time array `t`
```python
import xarray
import dascutils as du
D = xarray.open_dataset('filename.nc', group = 'DASC', autoclose = True)
times, pixel_brightness, X1, Y1 = du.getPixelBrightness(D, obstimes = t, obs_lon = X, obs_lat = Y, coordinates=True)
# times: time array of the closest images from DASC dataset
# X1, Y1: closest position of the pixel
```

### Plot an image
```python
from dascutils import plots as dascPlt

# Image only
dascPlt.imPlotXY(X, Y, img, args ...)
# Image with a trajectory
dascPlt.imPlotXY(X, Y, img, los_lon, los_lat, los_time, args ...)
```
![Alt text](tests/im.png?raw=true)
![Alt text](tests/im-los.png?raw=true)
### Make movies from DASC raw data files

Plots all wavelengths in subplots, for example:

```sh
PlotDASC tests/ -a cal/PKR_DASC_20110112
```
