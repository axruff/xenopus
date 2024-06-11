from OrsHelpers.viewLogger import ViewLogger
from OrsPlugins.orsimageloader import OrsImageLoader
from OrsHelpers.managedhelper import ManagedHelper
from OrsHelpers.datasethelper import DatasetHelper
from OrsHelpers.layoutpropertieshelper import LayoutPropertiesHelper
from OrsPythonPlugins.OrsObjectPropertiesList.OrsObjectPropertiesList import OrsObjectPropertiesList
from OrsPythonPlugins.OrsDerivedDataset.OrsDerivedDataset import OrsDerivedDataset
from OrsHelpers.roihelper import ROIHelper
from OrsHelpers.structuredGridLogger import StructuredGridLogger
from OrsHelpers.structuredGridHelper import StructuredGridHelper
from OrsHelpers.reporthelper import ReportHelper
from PIL import Image
import math
import json

from pathlib import Path, PureWindowsPath, PurePosixPath
import pandas as pd

#--------------------------------------------------------------
# Global settings
#--------------------------------------------------------------

#PATH_INPUT_FOLDER = 'z:\\tomo\\ershov\\xenopus\\_alignment\\'
#PATH_OUTPUT_INFO_FOLDER = 'z:\\tomo\\ershov\\xenopus\\_alignment\\'

PATH_INPUT_FOLDER       = 'z:\\projects\\code-vita\\Xenopus\\atlas_reduced\\'
PATH_OUTPUT_INFO_FOLDER = 'z:\\projects\\code-vita\\Xenopus\\atlas_reduced\\'
PATH_DATA_TABLE         = 'z:\\projects\\code-vita\\Xenopus\\atlas_reduced\\'

dataset_list = ['A2p1_16_5', 'A2p1_18_05', 'A2p0_20_01', 'A2p0_21_4', 'A2p2_22_05', 'A2p1_23_07']


#SPACING = 1.23e-06 # Pixel size in micrometers
SPACING = 0.001 # Pixel size in micrometers

current_dataset = 'no'
current_index = 0

def read_data_table(name='data_table_xenopus_align_crop.xls'):
    
    dt = pd.read_excel(PATH_DATA_TABLE + name, index_col=0)
    
    return dt
    

def read_dataset_list():
    print(f'Datasets')
    return

def load_next_dataset():
    
    global current_index
    global current_dataset
    
    #current_dataset = dataset_list[current_index]
    current_dataset = dt.iloc[current_index]['Naming']
    
    vol = load_volume(current_dataset + '.tif')
    
    current_index = current_index+1
    
    print(f'Dataset: "{current_dataset}" is loaded')
    
    return vol

def load_by_index(ind):
    
    current_index = ind
    
    current_dataset = dt.iloc[current_index]['Naming']
    
    vol = load_volume(current_dataset + '.tif')
    
    current_index = current_index+1
    
    print(f'Dataset: "{current_dataset}" is loaded')
    
    return vol

def load_by_index_and_copy(ind):
    
    vol = load_by_index(ind)
    rot = make_copy(vol)
    
    return vol, rot
     

def load_next_dataset_and_copy():
    
    vol = load_next_dataset()
    rot = make_copy(vol)
    
    return vol, rot

def get_volume_size(volume_path):

    im = Image.open(volume_path)
    return (im.size[0], im.size[1], im.n_frames)

def load_volume(volume_file_name = 'fA2p0_17_2_s_eig16_new_sagittal.tif'):

    fileNamesListElement = PATH_INPUT_FOLDER + volume_file_name
    fileNames = [fileNamesListElement]

    vol_size = get_volume_size(PATH_INPUT_FOLDER + volume_file_name)

    #xSize = 1048
    #ySize = 1140
    #zSize = 1116

    xSize = vol_size[0]
    ySize = vol_size[1]
    zSize = vol_size[2]
    tSize = 1
    minX = 0
    maxX = xSize -1
    minY = 0
    maxY = ySize -1
    minZ = 0
    maxZ = zSize -1
    xSampling = 1
    ySampling = 1
    zSampling = 1
    tSampling = 1
    xSpacing = SPACING
    ySpacing = SPACING
    zSpacing = SPACING
    slope = 1.0
    offset = 0.0
    dataUnit = ''
    invertX = False
    invertY = False
    invertZ = False
    axesTransformation = 0
    datasetName = volume_file_name
    convertFrom32To16bits = False
    dataRangeMin = 0.0
    dataRangeMax = 0.0
    frameCount = 1

    additionalInfo = 'PD94bWwgdmVyc2lvbj0iMS4wIj8+CjxJbWFnZUxvYWRlck1vZGVsIElzRGF0YVJHQj0iZmFsc2UiIFJHQk91dHB1dD0iMCIgSW52ZXJ0SW50ZW5zaXR5PSJmYWxzZSIgLz4K'


    output = OrsImageLoader.createDatasetFromFiles(fileNames=fileNames,
                                                xSize=xSize,
                                                ySize=ySize,
                                                zSize=zSize,
                                                tSize=tSize,
                                                minX=minX,
                                                maxX=maxX,
                                                minY=minY,
                                                maxY=maxY,
                                                minZ=minZ,
                                                maxZ=maxZ,
                                                xSampling=xSampling,
                                                ySampling=ySampling,
                                                zSampling=zSampling,
                                                tSampling=tSampling,
                                                xSpacing=xSpacing,
                                                ySpacing=ySpacing,
                                                zSpacing=zSpacing,
                                                slope=slope,
                                                offset=offset,
                                                dataUnit=dataUnit,
                                                invertX=invertX,
                                                invertY=invertY,
                                                invertZ=invertZ,
                                                axesTransformation=axesTransformation,
                                                datasetName=datasetName,
                                                convertFrom32To16bits=convertFrom32To16bits,
                                                dataRangeMin=dataRangeMin,
                                                dataRangeMax=dataRangeMax,
                                                frameCount=frameCount,
                                                additionalInfo=additionalInfo)

    volume_channel = output[0]
    ManagedHelper.publish(anObject=volume_channel)

    name = 'toplayout\\scene_0'
    isVisible = True
    
    DatasetHelper.setIsVisibleIn2DFromGenealogicalName(name=name,
                                                    dataset=volume_channel,
                                                    isVisible=isVisible)

  

    layoutFullName = 'toplayout\\scene_0'
    lutUUID = '7b00da82eefc11e68693448a5b87686a'
    aScalarValueTypeTag = ''
 
    LayoutPropertiesHelper.set3DLUTUUIDFromGenealogicalName(layoutFullName=layoutFullName,
                                                            anObject=volume_channel,
                                                            lutUUID=lutUUID,
                                                            aScalarValueTypeTag=aScalarValueTypeTag)


    return volume_channel

def make_copy(dataset):
    
    d = DatasetHelper.copyDataset(aDataset=dataset)
    
    d.setTitle(newVal='aligned', logging=True)
    
    d.publish(logging=True)
    
    name = 'toplayout\\scene_0'

    DatasetHelper.setIsVisibleIn2DFromGenealogicalName(name=name,
                                                       dataset=d,
                                                       isVisible=True)
    return d

def resample(orig_dataset, resampled_dataset):
    newTitle_3 = 'aligned (Resampled)'


    derivedDataset = OrsDerivedDataset.copyStructuredGridIntoAnotherShape(sourceStructuredGrid=resampled_dataset,
                                                                         referenceStructureGrid=orig_dataset,
                                                                         newTitle=newTitle_3)
    
    derivedDataset.publish(logging=True)
    
    name = 'toplayout\\scene_0'

    DatasetHelper.setIsVisibleIn2DFromGenealogicalName(name=name,
                                                       dataset=derivedDataset,
                                                       isVisible=True)
    
    return derivedDataset

def save_crop_box_info(im, file_name='crop'):
    v,d = StructuredGridHelper.getClipBoxForCurrentView(im)
    b = v.getBox(0)
    
    crop_info = {'x': math.floor(b.getOrigin().getX() / SPACING  + 1),
                'y': math.floor(b.getOrigin().getY() / SPACING + 1),
                'z': math.floor(b.getOrigin().getZ() / SPACING + 1),
                'w': math.floor(b.getDirection0Size() / SPACING + 0.5),
                'h': math.floor(b.getDirection1Size() / SPACING + 0.5),
                'd': math.floor(b.getDirection2Size() / SPACING + 0.5)
                    }
    
    with open(PATH_OUTPUT_INFO_FOLDER + file_name + '_crop_info.txt', "w") as fp:
        json.dump(crop_info, fp)  # encode dict into JSON
        
    print(f'Dataset: {file_name}: Croppping info is saved')
    
    
def save_rotation_info(im, file_name='rot'):
    b = im.getBox()
    
    x_dir = b.getDirection0()
    y_dir = b.getDirection1()
    z_dir = b.getDirection2()
    
    rotation_info = {'x_dir': {'x': x_dir.getX(), 'y': x_dir.getY(), 'z': x_dir.getZ()},
                     'y_dir': {'x': y_dir.getX(), 'y': y_dir.getY(), 'z': y_dir.getZ()},
                     'z_dir': {'x': z_dir.getX(), 'y': z_dir.getY(), 'z': z_dir.getZ()}
                    }
    
    with open(PATH_OUTPUT_INFO_FOLDER + file_name + '_rot_info.txt', "w") as fp:
        json.dump(rotation_info, fp)  # encode dict into JSON 
        
    print(f'Dataset: {file_name}: Rotation info is saved')
        
def clean(vol):
    DatasetHelper.deleteDataset(aDataset=vol)
    
def clean_all():
    global vol
    global rot
    global res
    
    DatasetHelper.deleteDataset(aDataset=vol)
    DatasetHelper.deleteDataset(aDataset=rot)  
    DatasetHelper.deleteDataset(aDataset=res)  
    
def save_all_info():
    global vol
    save_rotation_info(rot, current_dataset)
    save_crop_box_info(res, current_dataset)