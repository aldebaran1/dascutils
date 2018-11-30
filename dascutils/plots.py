from pathlib import Path
import xarray
import numpy as np
from datetime import timedelta, datetime
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.dates import DateFormatter
# = > no themis in DASC!
#try:
#    import themisasi.plots as themisplot
#except ImportError:
#    themisplot = None

def imPlotXYtrajectory(lon, lat, image, X, Y, T, figsize = (6,5), cmap = 'viridis', 
                       title = '', cbar = True, cbarlabel = '', xlabel = '', 
                       ylabel = '', returnfig = False):
    fig = imPlotXY(lon, lat, image, xlabel = xlabel, ylabel = ylabel, 
                 cbar = cbar, cbarlabel = cbarlabel, title = title,
                 returnfig = returnfig)
    if isinstance(X, list): 
        X = np.array(X)
        Y = np.array(Y)
        T = np.array(T)
    if isinstance(X, (int, float)):
        assert isinstance(T, datetime)
        plt.scatter(X, Y, s=20, c='xr')
        t0 = datetime.strftime(T, '%H:%S')
        plt.text(X + 1, Y, str(t0), weight='bold', color='r')
    else:
        assert isinstance(T[0], datetime)
        plt.scatter(X, Y, s=10, c='r')
        t0 = datetime.strftime(T[0], '%H:%S')
        t1 = datetime.strftime(T[-1], '%H:%S')
        plt.text(X[0] + 1, Y[0], str(t0), weight='bold', color='r')
        plt.text(X[-1] + 1, Y[-1], str(t1), weight='bold', color='r')
        
    if returnfig: return fig

def imPlotXY(lon, lat, image, figsize = (6,5), cmap = 'viridis', title = '',
             cbar = True, cbarlabel = '', xlabel = '', ylabel = '', 
             returnfig = False):
    fig = plt.figure(figsize=figsize)
    plt.title(title)
    plt.pcolormesh(lon, lat, image, cmap=cmap)
    if cbar: 
        if cbarlabel: 
            plt.colorbar().set_label(cbarlabel)
        else:
            plt.colorbar()
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    
    if returnfig: return fig

def linePlot(t, y, xlim = None, ylim = None, figsize=(8,4), c = '-b',
             xlabel = '', ylabel = '', returnfig = False):
    date_formatter = DateFormatter('%H:%M')
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111)
    ax.plot(t,y,c)
    
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    
    if xlim is not None: ax.set_xlim(xlim)
    if ylim is not None: ax.set_ylim(ylim)
    
    ax.grid(axis='y')
    ax.xaxis.set_major_formatter(date_formatter)
    
    if returnfig: return fig

def histogram_dasc(imgs: xarray.Dataset, odir=None):
    """
    creates per wavelength histograms
    the entries in list img correspond to wavelength, a 1-D array
    """
    if odir is not None:
        odir = Path(odir).expanduser()

    anyplot = False
    fg = plt.figure(figsize=(15, 5))
    axs = fg.subplots(1, 3)
    for a, i in zip(axs, imgs.data_vars):
        if i in ('az', 'el'):
            continue
        else:
            anyplot = True
        a.hist(imgs[i].dropna(dim='time', how='all').values.ravel(), bins=128)
        a.set_yscale('log')
        a.set_title(f'$\lambda={i}$ nm')
        a.set_xlabel('14-bit data numbers')

    if not anyplot:
        plt.close(fg)

    if odir:
        ofn = odir/'DASChistogram.png'
        print('writing', ofn, end='\r')
        fg.savefig(ofn, bbox_inches='tight')


def moviedasc(imgs: xarray.Dataset, odir: Path, cadence: float, rows=None, cols=None):

    if odir:
        print('writing to', odir)
        odir = Path(odir).expanduser()

    fg = plt.figure(figsize=(15, 5))

    if imgs.wavelength is not None:
        axs = np.atleast_1d(fg.subplots(1, len(np.unique(imgs.wavelength))))
    else:
        axs = [fg.gca()]

    if imgs.time.dtype == 'M8[ns]':
        time = [datetime.utcfromtimestamp(t/1e9) for t in imgs.time.values.astype(int)]
    else:
        time = imgs.time.values.astype(datetime)
# %% setup figures
    if 'unknown' not in imgs.data_vars:
        Hi = []
        Ht = []
        for ax, w, mm, c in zip(axs,
                                np.unique(imgs.wavelength),
                                ((350, 800), (350, 9000), (350, 900)),
                                ('b', 'g', 'r')):
            # ax.axis('off') #this also removes xlabel,ylabel
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_xlabel(f'{w} nm', color=c)

            Hi.append(ax.imshow(imgs[w].dropna(dim='time', how='all')[0],
                                vmin=mm[0], vmax=mm[1],
                                origin='lower',
                                norm=LogNorm(), cmap='gray'))

            Ht.append(ax.set_title('', color=c))
            # fg.colorbar(hi[-1],ax=a).set_label('14-bit data numbers')
#            if themisplot is not None:
#                themisplot.overlayrowcol(ax, rows, cols)

        fg.tight_layout(h_pad=1.08)  # get rid of big white space in between figures
    else:
        ax = axs[0]
        ax.set_xticks([])
        ax.set_yticks([])
        hi = ax.imshow(imgs['unknown'][0],
                       vmin=(350, 10000),
                       origin='lower',
                       norm=LogNorm(), cmap='gray')

        ht = ax.set_title('')
#        if themisplot is not None:
#            themisplot.overlayrowcol(ax, rows, cols)
# %% loop
    print('generating video until', time[-1])
    t = time[0]
    dt = timedelta(seconds=cadence)
    while t <= time[-1]:
        if 'unknown' not in imgs.data_vars:
            for w, hi, ht in zip(np.unique(imgs.wavelength), Hi, Ht):
                im = imgs[w].dropna(dim='time', how='all').sel(time=t, method='nearest')
                hi.set_data(im)
                try:
                    ht.set_text(str(im.time.values))
                except OSError:  # file had corrupted time
                    ht.set_text('')
        else:
            im = imgs['unknown'].sel(time=t, method='nearest')
            hi.set_data(im)
            try:
                ht.set_text(str(im.time.values))
            except OSError:  # file had corrupted time
                ht.set_text('')

        plt.draw(), plt.pause(0.05)  # the pause avoids random crashes
        t += dt

        if odir:
            ofn = odir / (str(t)+'.png')
            print('saving', ofn, end='\r')
            fg.savefig(ofn, bbox_inches='tight', facecolor='k')
