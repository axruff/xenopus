import os
import time
from scipy.spatial.transform import Rotation as R
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import multiprocessing as mp

import matplotlib.patches as patches
import math

#import cv2
from PIL import Image
import pandas as pd

import SimpleITK as sitk
from torchio.transforms import Affine
from torchio import Image

from pathlib import Path, PureWindowsPath, PurePosixPath

from bs4 import BeautifulSoup
import json


table_path = '/mnt/LSDF/tomo/ershov/xenopus/_alignment/'

def convert_path(path):
    prefix = '/mnt/HD-LSDF/Xenopus/'
    pw = PureWindowsPath(path)
    #print(pw)
    pl = PurePosixPath(prefix, *pw.parts[1:])

    return pl

def get_datasets_size(dt):

    total_size = 0.0  

    for i in range(len(dt)):
    
        path = dt.iloc[i]['path']
        path = convert_path(path)
 
        file_size = os.path.getsize(path)
        file_size = file_size / 1e9

        total_size = total_size + file_size

        print('File size: ', total_size)

    return total_size

def process_dataset(i):

    path = dt.iloc[i]['path']
    path = convert_path(path)
    dataset = dt.iloc[i]['Naming']

    print(f'Reading: {dataset}')

    start = time.time()

    sitk_image = sitk.ReadImage(str(path))

    print('OK')
    elapsed = (time.time() - start) / 60
    print(f'Reading time: {elapsed} min')

    image_data = sitk.GetArrayFromImage(sitk_image)

    start = time.time()
    
    x2,y2,z2 = read_rotation_info(align_path / f'{dataset}_rot_info.txt')
    cr = read_crop_info(align_path / f'{dataset}_crop_info.txt')
    
    
    image_rotated = rotate_dataset(dataset, image_data, [z2,y2,x2])

    scale = 2.0

    image_cropped = image_rotated[math.floor(cr['z']*scale):math.floor(cr['z']*scale)+math.floor(cr['d']*scale),
                                  math.floor(cr['y']*scale):math.floor(cr['y']*scale)+math.floor(cr['h']*scale),
                                  math.floor(cr['x']*scale):math.floor(cr['x']*scale)+math.floor(cr['w']*scale)]

    print('Cropped shape', image_cropped.shape)

    print('OK')
    elapsed = (time.time() - start) / 60
    print(f'Transform time: {elapsed} min')

    start = time.time()

    #sitk_image = sitk.GetImageFromArray(image_cropped.astype('uint8'))
    sitk_image = sitk.GetImageFromArray(image_cropped)
    sitk.WriteImage(sitk_image, res_path / f'{dataset}.tif')

    #plot_volume_slices(image_rotated)
    plot_volume_slices_4_views_as_dragonfly(image_cropped, dataset)

    print('OK')
    elapsed = (time.time() - start) / 60
    print(f'Saving time: {elapsed} min')


def read_crop_info(file_name):
    
    with open(file_name, "r") as fp:
        crop_info = json.load(fp)
        
    return crop_info

def read_rotation_info(file_name):
    
    with open(file_name, "r") as fp:
        rot = json.load(fp)
        
        
        #rotation_info = {'x_dir': {'x': x_dir.getX(), 'y': x_dir.getY(), 'z': z_dir.getZ()},
        #             'y_dir': {'x': y_dir.getX(), 'y': y_dir.getY(), 'z': y_dir.getZ()},
        #             'z_dir': {'x': z_dir.getX(), 'y': z_dir.getY(), 'z': z_dir.getZ()}
        #            }
        
    x = [rot['x_dir']['x'], rot['x_dir']['y'], rot['x_dir']['z']]
    y = [rot['y_dir']['x'], rot['y_dir']['y'], rot['y_dir']['z']]
    z = [rot['z_dir']['x'], rot['z_dir']['y'], rot['z_dir']['z']]
    
  
    return x,y,z
    

def read_dragonfly_transform(file_name):
    
    with open(str(file_name), 'r') as f:
        data = f.read()

#print(data[12:])

    xml_data = BeautifulSoup(data[12:], "xml")

    #print(xml_data)

    x_dir = xml_data.find('direction0')
    y_dir = xml_data.find('direction1')
    z_dir = xml_data.find('direction2')

    x2 = [float(x_dir.get('x')), float(x_dir.get('y')), float(x_dir.get('z'))]
    y2 = [float(y_dir.get('x')), float(y_dir.get('y')), float(y_dir.get('z'))]
    z2 = [float(z_dir.get('x')), float(z_dir.get('y')), float(z_dir.get('z'))]
    
    f.close()
    
    return x2,y2,z2


def save_np_as_multitiff_stack(volume, file_name):
    
    imlist = []
    for i in range(volume.shape[0]):
        imlist.append(Image.fromarray(volume[i]))

    imlist[0].save(file_name, save_all=True, append_images=imlist[1:])
    
    del imlist 
    
def rotate_dataset(dataset, image_data, angles):

    x = [1, 0, 0]
    y = [0, 1, 0]
    z = [0, 0, 1]

    #x2,y2,z2 = read_dragonfly_transform(path / 'transform.ORSObject')

    res_rot = R.align_vectors(angles, [z,y,x])
    rotation_degrees = res_rot[0].as_euler('zyx', degrees=True)

    #res_rot = R.align_vectors([x2,y2,z2],[x,y,z])
    #rotation_degrees = res_rot[0].as_euler('xyz', degrees=True)


    print('Original:', rotation_degrees)

    #degrees = -rotation_degrees
    degrees = -rotation_degrees
    #degrees[0] = (degrees[0] - 180)
    #degrees[1] = -degrees[1]
    #degrees[2] = -degrees[2] 

    # [z,y,x]
    #degrees = [0,0,-10]

    rot_x = degrees[2]
    rot_y = degrees[1]
    rot_z = degrees[0]

    print('Corrected:', degrees)

    if True:

        img_rotation = Affine(scales=[1.0, 1.0, 1.0], degrees=degrees, translation=[0,0,0],
                                      center='image')

        img_rotation_x = Affine(scales=[1.0, 1.0, 1.0], degrees=[0,0,rot_x], translation=[0,0,0],
                                      center='image')
        img_rotation_y = Affine(scales=[1.0, 1.0, 1.0], degrees=[0,rot_y,0], translation=[0,0,0],
                                      center='image')
        img_rotation_z = Affine(scales=[1.0, 1.0, 1.0], degrees=[rot_z,0,0], translation=[0,0,0],
                                      center='image')


        #pos_rotation = sitk.Euler3DTransform()
        #pos_rotation.SetRotation(*rotation_radians)
  
        print('Image shape', image_data.shape)

        #offset_z = 450
        #image_data = image_data[offset_z:,:,:]

        #image_rotated = img_rotation(np.expand_dims(image_data, axis=0))[0]

        image_rotated_z = img_rotation_z(np.expand_dims(image_data, axis=0))[0]
        image_rotated_zy = img_rotation_y(np.expand_dims(image_rotated_z, axis=0))[0]
        image_rotated = img_rotation_x(np.expand_dims(image_rotated_zy, axis=0))[0]

        print('Image shape', image_rotated.shape)
        print(image_rotated.dtype)

        #result_image = sitk.GetImageFromArray(image_rotated.transpose(2, 1, 0))
        print('Done!')
        
        return image_rotated
    

def plot_volume_slices_4_views_as_dragonfly(image, dataset):
    
    fig = plt.figure(figsize= (10,10), layout="tight")

    gs = GridSpec(2, 2, figure=fig)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[1, 0])
    ax3 = fig.add_subplot(gs[0, 1])
    ax4 = fig.add_subplot(gs[1, 1])

    sx = image.shape[2]
    sy = image.shape[1]
    sz = image.shape[0]

    ax1.imshow(np.zeros((sx,sy)), cmap='gray')
    ax1.axis('off')
    #plt.show()

    ax2.imshow(image[int(sz/2)], cmap='gray')
    ax2.axis('off')
    #rect = patches.Rectangle((math.floor(cr['x']/2), math.floor(cr['y']/2)), math.floor(cr['w']/2), math.floor(cr['h']/2), linewidth=1, edgecolor='g', facecolor='none')
    #ax2.add_patch(rect)
    ax2.plot(math.floor(sx/2),math.floor(sy/2),'go') 
    #plt.show()

    print(sy)
    ax3.imshow(image[:,int(sy/2),:], cmap='gray')
    ax3.axis('off')
    #rect = patches.Rectangle((math.floor(cr['x']/2), math.floor(cr['z']/2)), math.floor(cr['w']/2), math.floor(cr['d']/2), linewidth=1, edgecolor='g', facecolor='none')
    #ax3.add_patch(rect)
    ax3.plot(math.floor(sx/2),math.floor(sz/2),'go') 
    #plt.show()

    ax4.imshow(image[:,:,int(sx/2)], cmap='gray')
    ax4.axis('off')
    #rect = patches.Rectangle((math.floor(cr['y']/2), math.floor(cr['z']/2)), math.floor(cr['h']/2), math.floor(cr['d']/2), linewidth=1, edgecolor='g', facecolor='none')
    #ax4.add_patch(rect)
    ax4.plot(math.floor(sy/2),math.floor(sz/2),'go') 
    #plt.show()

    #plt.show()
    fig.savefig(preview_path / f'{dataset}_new.png')



if __name__ == "__main__":

    table_path = '/mnt/LSDF/pn-reduction/atlas_xenopus/'
    align_path = Path("/mnt/LSDF/pn-reduction/atlas_xenopus/alignment_info/")
    res_path = Path("/mnt/LSDF/pn-reduction/atlas_xenopus/32bit/")
    preview_path = Path("/mnt/LSDF/pn-reduction/atlas_xenopus/preview/")

    # Check datasets size
    dt = pd.read_excel(table_path + 'data_table_xenopus_align_crop.xls', index_col=0)
    #sz = get_datasets_size(dt)
    #print('Total size', sz)

    dataset_list = [75]

    pool = mp.Pool(1)
    res = pool.map(process_dataset, dataset_list)
