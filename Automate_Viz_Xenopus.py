from OrsHelpers.viewLogger import ViewLogger
from OrsPlugins.orsimageloader import OrsImageLoader
from OrsHelpers.managedhelper import ManagedHelper
from OrsHelpers.datasethelper import DatasetHelper
from OrsHelpers.layoutpropertieshelper import LayoutPropertiesHelper
from OrsPythonPlugins.OrsObjectPropertiesList.OrsObjectPropertiesList import OrsObjectPropertiesList
from OrsHelpers.roihelper import ROIHelper
from OrsHelpers.structuredGridLogger import StructuredGridLogger
from OrsHelpers.reporthelper import ReportHelper

from PIL import Image


#--------------------------------------------------------------
# Global settings
#--------------------------------------------------------------

#PATH_INPUT_FOLDER = 'C:/Users/fe0968/Documents/data/xenopus/Alexey_dragonscripts/'
#PATH_OUTPUT_FOLDER = 'C:/Users/fe0968/Documents/data/xenopus/Alexey_dragonscripts/output/'

PATH_INPUT_FOLDER = 'c:/Users/fe0968/Documents/data/medaka/landmarks/'

SPACING = 1.23e-06 # Pixel size in micrometers

SCREENSHOT_WIDTH = 797
SCREENSHOT_HEIGHT = 499

DISTANCE_DEFAULT = -0.001693

#SCREENSHOT_WIDTH = 1200
#SCREENSHOT_HEIGHT = 1000


#--------------------------------------------------------------
# Predefined camera views and crop boxes
#--------------------------------------------------------------


def get_camera_from_view(volume_size=(500, 500, 500), view='Z', distance= DISTANCE_DEFAULT):

    X_size = volume_size[0]
    Y_size = volume_size[1] 
    Z_size = volume_size[2]

    camera = None

    if view == 'Z' or view == 'side' or view == 'sagittal':
        camera = camera_Z_sagittal(X_size, Y_size, Z_size, distance)

    if view == 'Y' or view == 'top' or view == '?':
        camera = camera_Y_top(X_size, Y_size, Z_size, distance)

    if view == 'X' or view == 'front' or view == '??':
        camera = camera_X_front(X_size, Y_size, Z_size, distance)

    if not camera:
        print('Camera view is not specified correctly')
        return

    return camera


def get_crop_box_from_view(slice, volume_size = (500, 500, 500), view='Z'):

    X_size = volume_size[0]
    Y_size = volume_size[1] 
    Z_size = volume_size[2]

    if view == 'Z' or view == 'side' or view == 'sagittal':
        return orsBox(

            origin=orsVect(-SPACING/2.0, -SPACING/2.0, slice*SPACING),

            dir0=orsVect(1, 0, 0), 
            dir0Length=X_size*SPACING, 
            dir0Spacing=SPACING, 

            dir1=orsVect(0, 1, 0), 
            dir1Length=Y_size*SPACING, 
            dir1Spacing=SPACING, 

            dir2=orsVect(0, 0, 1), 
            dir2Length=(Z_size- slice)*SPACING, 
            dir2Spacing=SPACING
        )

    if view == 'Y' or view == 'top' or view == '?':
        return orsBox(

            origin=orsVect(-SPACING/2.0, (Y_size- slice)*SPACING, -SPACING/2.0),

            dir0=orsVect(1, 0, 0), 
            dir0Length=X_size*SPACING, 
            dir0Spacing=SPACING, 

            dir1=orsVect(0, 1, 0), 
            dir1Length=slice*SPACING, 
            dir1Spacing=SPACING, 

            dir2=orsVect(0, 0, 1), 
            dir2Length=Z_size*SPACING, 
            dir2Spacing=SPACING
        )

    if view == 'X' or view == 'front' or view == '??':
        return orsBox(

            origin=orsVect(slice*SPACING, -SPACING/2.0, -SPACING/2.0),

            dir0=orsVect(1, 0, 0), 
            dir0Length=(X_size- slice)*SPACING, 
            dir0Spacing=SPACING, 

            dir1=orsVect(0, 1, 0), 
            dir1Length=Y_size*SPACING, 
            dir1Spacing=SPACING, 

            dir2=orsVect(0, 0, 1), 
            dir2Length=Z_size*SPACING, 
            dir2Spacing=SPACING
        )

    print('No bbox')
    return




def camera_X_front(X_size=500, Y_size=500, Z_size=500, distance = DISTANCE_DEFAULT):

    return orsCamera(
        dir=orsVect(1, -0, -0), 
        pos=orsVect(distance, Y_size*SPACING/2.0, Z_size*SPACING/2.0), 
        up=orsVect(-0, -1, -0), 
        pivot=orsVect(X_size*SPACING/2.0, Y_size*SPACING/2.0, Z_size*SPACING/2.0), 
        vHeight=319, vWidth=646, vTopLefX=0, vTopLeftY=0, vNear=1e-06, vFar=0.35055, 
        useOrtho=False, orthoZoom=1, focalLength=1, depthOfField=1, 
        angleOfView=0.785398163, 
        normalizationTranslationMatix=orsMatrix(1, 0, 0, -0.000643905, 0, 1, 0, -0.000700485, 0, 0, 1, -0.000685725, 0, 0, 0, 1), 
        normalizationRotationMatix=orsMatrix(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1), 
        normalizationScaleMatix=orsMatrix(713.165026, 0, 0, 0, 0, 713.165026, 0, 0, 0, 0, 713.165026, 0, 0, 0, 0, 1)
    )


def camera_Y_top(X_size=500, Y_size=500, Z_size=500, distance = DISTANCE_DEFAULT):

    return orsCamera(
        dir=orsVect(0, 1, 0), 
        pos=orsVect(X_size*SPACING/2.0, distance, Z_size*SPACING/2.0), 
        up=orsVect(-1, 0, 0), 
        pivot=orsVect(X_size*SPACING/2.0, Y_size*SPACING/2.0, Z_size*SPACING/2.0), 
        vHeight=319, vWidth=646, vTopLefX=0, vTopLeftY=0, vNear=1e-06, vFar=0.35055, 
        useOrtho=False, orthoZoom=1, focalLength=1, depthOfField=1, 
        angleOfView=0.785398163, 
        normalizationTranslationMatix=orsMatrix(1, 0, 0, -0.000643905, 0, 1, 0, -0.000700485, 0, 0, 1, -0.000685725, 0, 0, 0, 1), 
        normalizationRotationMatix=orsMatrix(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1), 
        normalizationScaleMatix=orsMatrix(713.165026, 0, 0, 0, 0, 713.165026, 0, 0, 0, 0, 713.165026, 0, 0, 0, 0, 1)
    )


def camera_Z_sagittal(X_size=500, Y_size=500, Z_size=500, distance = DISTANCE_DEFAULT):

    return orsCamera(
    dir=orsVect(0, 0, 1), 
    pos=orsVect(X_size*SPACING/2.0, Y_size*SPACING/2.0, distance), 
    up=orsVect(0, -1, 0), 
    pivot=orsVect(X_size*SPACING/2.0, Y_size*SPACING/2.0, Z_size*SPACING/2.0), 
    vHeight=210, vWidth=646, vTopLefX=0, vTopLeftY=0, vNear=1e-06, vFar=0.35055, 
    useOrtho=False, orthoZoom=1, focalLength=1, depthOfField=1, 
    angleOfView=0.785398163, 
    normalizationTranslationMatix=orsMatrix(1, 0, 0, -0.000643905, 0, 1, 0, -0.000700485, 0, 0, 1, -0.000685725, 0, 0, 0, 1), 
    normalizationRotationMatix=orsMatrix(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1), 
    normalizationScaleMatix=orsMatrix(713.165026, 0, 0, 0, 0, 713.165026, 0, 0, 0, 0, 713.165026, 0, 0, 0, 0, 1)
)


def get_volume_size(volume_path):

    im = Image.open(volume_path)
    return (im.size[0], im.size[1], im.n_frames)


def set_camera(volume_channel, view = 'Z', distance = DISTANCE_DEFAULT):

    aName_3 = 'toplayout\\scene_0\\0\\3D'

    X_size = volume_channel.getXSize() 
    Y_size = volume_channel.getYSize() 
    Z_size = volume_channel.getZSize() 

    camera = get_camera_from_view(volume_size=(X_size, Y_size, Z_size), view=view, distance=distance)

    ViewLogger.setCameraFromLayoutGenealogicalName(aName=aName_3,
                                                camera=camera)


def load_volume_and_label(volume_file_name = 'fA2p0_17_2_s_eig16_new_sagittal.tif', label_file_name = 'Segmentation_st16.ORSObject'):

    volume = load_volume(volume_file_name)
    label = load_label(label_file_name)

    return volume, label



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





def load_label(label_file_name='Segmentation_st16.ORSObject'):

    # Load data from ORS file
    fname = PATH_INPUT_FOLDER + label_file_name

    #guidsListElement = '54ECDDD4AE364AD5B2654377D339334ECxvLabeledMultiROI_XXX'
    #guids = [guidsListElement]

    #importedObjects = OrsObjectPropertiesList.importSpecificObjectsFromFileAndPublish(fname=fname,
    #                                                                                guids=guids,
    #                                                                                progress=None)

    importedObjects = OrsObjectPropertiesList.importORSObjectsFromFileAndPublish(filenames=[fname],                                                                   
                                                                                   progress=None)


    label_channel = importedObjects[0]
  
    # Show labels
    
    name = 'toplayout\\scene_0'
    isVisible = True

    ROIHelper.setIsVisibleIn2DFromGenealogicalName(name=name,
                                                aROI=label_channel,
                                                isVisible=isVisible)

  
    name_3 = 'toplayout\\scene_0\\0\\3D'
    isVisible_3 = True

    ROIHelper.setIsVisibleIn3DFromGenealogicalName(name=name_3,
                                                aROI=label_channel,
                                                isVisible=isVisible_3)
    return label_channel



def make_slicing(image_channel, multiROI=None, view='Z', slices_list=None):

    view_name = 'toplayout\\scene_0\\0\\3D'

    X_size = image_channel.getXSize() 
    Y_size = image_channel.getYSize() 
    Z_size = image_channel.getZSize() 

    StructuredGridLogger.setClipBoxVisibilityOfChannelFromLayoutGenealogicalName(aName=view_name,
                                                                             channel=image_channel,
                                                                             isVisible=True)
    if multiROI:
        StructuredGridLogger.setClipBoxVisibilityOfROIFromLayoutGenealogicalName(aName=view_name,
                                                                             aROIOrMultiROI=multiROI,
                                                                             isVisible=True)


    slices = []

    #slices_X = [213, 513, 744]
    #slices_Y = [990, 714, 597]
    #slices_Z = [567, 468]

    if slices_list is not None: 

        if view == 'Z' or view == 'side' or view == 'sagittal':
            slices = [0]
            slices_list.reverse()
            slices.extend(slices_list)

        if view == 'Y' or view == 'top' or view == '?':
            slices = [0]
            slices.extend(slices_list)

        if view == 'X' or view == 'front' or view == '??':
            slices = [0]
            slices.extend(slices_list)

    else:
        print('No slices are specified!')

    #print('Slices:', slices)

    


    # New Box
    # aBox = orsBox(
    #     origin=orsVect(-SPACING/2.0, 0.000435163659, -SPACING/2.0), 

    #     dir0=orsVect(1, 0, 0), 
    #     dir0Length=0.00128904, 
    #     dir0Spacing=1.23e-06, 
        
    #     dir1=orsVect(0, 1, 0),     
    #     dir1Length=0.000966421341, 
    #     dir1Spacing=1.23e-06, 

    #     dir2=orsVect(0, 0, 1), 
    #     dir2Length=0.00137268, 
    #     dir2Spacing=1.23e-06
    # )


    # Perform slicing using Visual Box

    c = 0

    for slice in slices:

        aBox = get_crop_box_from_view(slice, volume_size = (X_size, Y_size, Z_size), view=view) 

        StructuredGridLogger.setVisualBoxOfChannelFromLayoutGenealogicalName(aName=view_name,
                                                                            channel=image_channel,
                                                                            aBox=aBox)


        StructuredGridLogger.setClipBoxVisibilityOfChannelFromLayoutGenealogicalName(aName=view_name,
                                                                                    channel=image_channel,
                                                                                    isVisible=False)


        if multiROI:
            StructuredGridLogger.setVisualBoxOfROIFromLayoutGenealogicalName(aName=view_name, 
                                                                            aROIOrMultiROI=multiROI, 
                                                                            aBox=aBox)

            StructuredGridLogger.setClipBoxVisibilityOfROIFromLayoutGenealogicalName(aName=view_name,
                                                                                        aROIOrMultiROI=multiROI,
                                                                                        isVisible=False)


        path_data = PATH_OUTPUT_FOLDER + '\\snapshot_' + view + '_' +  str(c).zfill(2) + '.png'

        ReportHelper.captureSnapshot(viewName=view_name,
                                    filename=path_data,
                                    xSize=SCREENSHOT_WIDTH,
                                    ySize=SCREENSHOT_HEIGHT)

        c+=1



    # Reset Clip box
    StructuredGridLogger.resetVisualBoxOfChannelFromLayoutGenealogicalName(aName=view_name,
                                                                        channel=image_channel)

    # Set camera to default mode
    set_camera(image_channel, view = view)


#def screenshot()



    
def screenshot(image_channel, multiROI=None, view='Z', slices = None, distance = DISTANCE_DEFAULT):

    set_camera(image_channel,view=view, distance=distance)
    make_slicing(image_channel, multiROI, view=view, slices_list=slices)


def all_screenshots(image_channel, multiROI=None, slices_first = None, slices_second = None, slices_third = None, distance = DISTANCE_DEFAULT):

    screenshot(image_channel, multiROI, view='X', slices =slices_second, distance=distance)
    screenshot(image_channel, multiROI, view='Y', slices =slices_first, distance=distance)
    screenshot(image_channel, multiROI, view='Z', slices =slices_third, distance=distance)
