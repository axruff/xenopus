import os.path
import pandas as pd

from pathlib import Path, PureWindowsPath, PurePosixPath
import tifffile

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import math

from binscale.scaler import Scaler
from binscale.converter import Converter

import time

import multiprocessing as mp

import numpy as np
np.bool = np.bool_

def read_tifffile(file_, lazy=False):
    descriptor = tifffile.TiffFile(file_)
    img = tifffile.memmap(file_) if lazy else tifffile.imread(file_)
    full_len = len(descriptor.pages)
    loaded_len = len(img)

    # for handling multi-page tiffs
    if loaded_len < full_len:
        if not lazy:
            img = np.array([page.asarray() for page in descriptor.pages])

        else:
            final_shape = (full_len, *img.shape[1:])
            with tempfile.NamedTemporaryFile() as f:
                img = np.memmap(f.name, dtype=img.dtype, mode='w+', shape=final_shape)
                for i, page in enumerate(descriptor.pages):
                    img[i] = page.asarray()
                    img = np.memmap(f.name, dtype=img.dtype, mode='r+', shape=final_shape)

    return img


def make_figure(im, file_path):
    fig = plt.figure(figsize= (10,10), layout="tight")

    gs = GridSpec(2, 2, figure=fig)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[1, 0])
    ax3 = fig.add_subplot(gs[0, 1])
    ax4 = fig.add_subplot(gs[1, 1])
    
    sz = math.floor(im.shape[0] / 2)
    sy = math.floor(im.shape[1] / 2)
    sx = math.floor(im.shape[2] / 2)


    ax1.imshow(np.zeros((2*sy,2*sx)), cmap='gray')
    ax1.axis('off')
    #plt.show()

    ax2.imshow(im[sz], cmap='gray')
    ax2.axis('off')
   
    ax3.imshow(im[:,sy,:], cmap='gray')
    ax3.axis('off')
    
    ax4.imshow(im[:,:,sx], cmap='gray')
    ax4.axis('off')
    
    #plt.show()

    fig.savefig(file_path)

def process_dataset(i):
    
    path = dt.iloc[i]['path']
    name = dt.iloc[i]['Naming']

    pw = PureWindowsPath(path)
    #print(pw)
    
    pl = PurePosixPath(prefix, *pw.parts[1:])
    
    if os.path.isfile(pl):
        print('Name:', name, ' Path:', pl)
    else:
        print('!!!!!!Problem ', 'Name:', name, ' Path:', pl)
        
        
    im = read_tifffile(pl)
    #end = time.time()
    print('Read Ok: ', name)
        
    if False:
        # Read
        #start = time.time()
        im = read_tifffile(pl)
        #end = time.time()
        #print('Read Ok: ', name)


        # Scale
        #start = time.time()
        sc = Scaler(0.5)
        im_sc = sc(im)
        #end = time.time()
        #print('Scaling: ', round((end-start)/60,1))

        #Convert
        #start = time.time()
        conv = Converter()
        im_8 = conv(im_sc[0])
        #end = time.time()
        #print('Converting: ', round((end-start)/60,1))

        #start = time.time()
        tifffile.imsave(save_path + f'{name}.tif', im_8[0])
        #end = time.time()
        #print('Saving: ', round((end-start)/60,1))
        
        make_figure(im_8[0], save_path + f'preview/preview_{name}.png')
        
        print(f'Finished: {name}')
        

        
dt = pd.read_excel('Liste Alexey erste Runde Rotation.xlsx', index_col=0) 


if __name__ == "__main__":
    
    prefix = '/mnt/HD-LSDF/Xenopus/'   
    save_path = '/mnt/LSDF/projects/code-vita/Xenopus/atlas_reduced/'
    
    pool = mp.Pool(4)
    #res = pool.map(process_dataset, range(len(dt)))
    #res = pool.map(process_dataset, range(5))
    res = pool.map(process_dataset, [31,32])
    
    print('Finished')
    



