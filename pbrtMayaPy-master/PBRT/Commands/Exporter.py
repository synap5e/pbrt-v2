# ------------------------------------------------------------------------------
# PBRT exporter for Maya 2013
#
# Based on a Python LuxMaya translation by Doug Hammond, in turn base on translation of the c++ luxmaya exporter, 
# in turn based on original maya-pbrt c++ exporter by Mark Colbert
#
# This file is licensed under the GPL (the original exporter uses that license)
# http://www.gnu.org/licenses/gpl-3.0.txt
#
# $Id$
#
# ------------------------------------------------------------------------------
#
# This file contains the main Exporter class that has the main graph iterator in DoIt()
#
# ------------------------------------------------------------------------------


import os
os.altsep = '/'
from maya import OpenMaya
from maya import OpenMayaUI
from maya import OpenMayaAnim
from maya import cmds


import PBRT.ExportModules.Camera as PBRTCamera
import PBRT.ExportModules.RenderGlobals as PBRTGlobals
import PBRT.ExportModules.MeshOpt as PBRTMesh
import PBRT.ExportModules.Light as PBRTLight
import PBRT.ExportModules.Material as PBRTMaterial
import PBRT.ExportModules.Locator as PBRTLocator
import PBRT.ExportModules.Volume as PBRTVolume

# Those reloads can be uncommented, to reload those modules without restating Maya
# reload(PBRTCamera)
# reload(PBRTGlobals)
# reload(PBRTMesh)
# reload(PBRTLight)
# reload(PBRTMaterial)
# reload(PBRTLocator)


class consoleProgress:
    cProgress = 0
    tProgress = 0
    def advanceProgress(self, progress):
        self.cProgress = progress
        print 'Progress: %i / %i' % (self.cProgress, self.tProgress)
    def isCancelled(self):
        return False
    def setTitle(self, string):
        print string
    def setProgressStatus(self, string):
        print string
    def endProgress(self):
        print "Done!"

class Exporter:
    """
    Scene iterator-controller for export process.
    This class exports the current frame according to the given parameters.
    It has the main doIt method as well as a set of scene graph iterators 
    """
    
    
    def __init__(self,
                 sceneFileName,
                 imageSaveName,
                 renderWidth,
                 renderHeight,
                 renderCameraName,
                 verbosity):
        "basic initialization of member variables"
        #OpenMaya.MGlobal.displayInfo("initializing exporter " + str(type(sceneFileNameIn)) )
        
        self.sceneFileName = sceneFileName
        self.imageSaveName = imageSaveName
        self.renderWidth = renderWidth
        self.renderHeight = renderHeight
        self.renderCameraName = renderCameraName
        self.verbosity = verbosity
        
        self.syntheticFileName = sceneFileName.replace(".pbrt", ".synthetic.pbrt")
        self.localFileName = sceneFileName.replace(".pbrt", ".local.pbrt")
        self.volumeFileName = sceneFileName.replace(".pbrt", ".volume.pbrt")
        self.areaLightsFileName = sceneFileName.replace(".pbrt", ".areaLgt.pbrt")
        sceneFilePathParts = sceneFileName.split( os.altsep ).pop()
        self.sceneFilePath = os.altsep.join(sceneFilePathParts) + os.altsep
        
        self.tempDagPath = OpenMaya.MDagPath()  # temp storage for dagPaths in iterators
        
        if verbosity>2:
            self.debug = True # displays output on stdout, no file write
            self.dprint("Debug mode. No file would be written", verbosity)
        else:
            self.debug = False
    
    def doIt(self):
        """
        Class entry point. Starts the frame export process.
        """
            
        
        if OpenMaya.MGlobal.mayaState() == OpenMaya.MGlobal.kInteractive:
            self.mProgress = OpenMayaUI.MProgressWindow()
        else:
            self.mProgress = consoleProgress()
        
        
        self.log("Starting pbrt export:")
        
        if not self.debug:
            try:
                self.sceneFileHandle    = open(self.sceneFileName, "wb")
            except:
                OpenMaya.MGlobal.displayError( "Failed to open files for writing\n" )
                raise
        
        
        #
        # WRITE EXTERNAL FILES
        #
        includeFileList = []
        
        
        self.sceneFileHandle.write( PBRTGlobals.RenderGlobals(self.renderWidth, self.renderHeight, self.imageSaveName).exportStr() )
        
        
        # Output the specified camera.
        cameraPath = self.findRenderCamera()
        if not cameraPath:
            OpenMaya.MGlobal.displayError("Could not find the camera")
            return
            
        
        self.sceneFileHandle.write(PBRTCamera.Camera(cameraPath,self.renderWidth, self.renderHeight).exportStr() )
        
        # obtain camera settings and write to file
        self.dprint( "Camera code: " )
        self.dprint( self.renderCameraName )
        self.dprint( "-------------" )

        currentFrame = OpenMayaAnim.MAnimControl.currentTime().asUnits(OpenMaya.MTime.kFilm)
        self.sceneFileHandle.write('FrameNumber "float frame" [' + str(currentFrame) + ']' + os.linesep)

        if not self.debug:
            self.sceneFileHandle.write( os.linesep + 'WorldBegin' + os.linesep + os.linesep )

        self.sceneFileHandle.write('\t# background image' + os.linesep)
        self.sceneFileHandle.write('\tDifferentialBackground' + os.linesep)
        self.sceneFileHandle.write('\t"string filename"["textures/background2.exr"]' + os.linesep)
        self.sceneFileHandle.write('\t"string type" "exponential"' + os.linesep)
        self.sceneFileHandle.write('\t"float exposure"[5]' + os.linesep)


        self.log("Camera written")

        # POLYGON MESHES
        
        if cmds.getAttr( 'pbrt_settings.scene_export_meshes' ) == 1:
            try:        
                self.meshLocalFileHandle = open(self.localFileName, "wb")
                self.meshSyntheticFileHandle = open(self.syntheticFileName, "wb")
            except:
                OpenMaya.MGlobal.displayError( "Failed to open file %s for writing\n"%self.syntheticFileName )
                raise  
        else:
            self.meshLocalFileHandle = 0
            self.meshSyntheticFileHandle = 0

        if cmds.getAttr( 'pbrt_settings.scene_export_arealights' ) == 1:
            try:        
                self.areaLightsFileHandle = open(self.areaLightsFileName, "wb")
            except:
                OpenMaya.MGlobal.displayError( "Failed to open file %s for writing\n"%self.areaLightsFileName )
                raise  
        else:
            self.areaLightsFileHandle = 0

        if cmds.getAttr('pbrt_settings.scene_export_volumes') == 1:
            try:
                self.volumeFileHandle = open(self.volumeFileName, "wb")
            except:
                OpenMaya.MGlobal.displayError("Failed to open file %s for writing\n" % self.volumeFileName)
                raise
        else:
            self.volumeFileHandle = 0


                # loop through meshes
        areaLightsWereWritten = 0
        self.exportType(OpenMaya.MFn.kMesh, PBRTMesh.MeshOpt.GeoFactory, "Mesh", (self.meshLocalFileHandle, self.meshSyntheticFileHandle, self.areaLightsFileHandle) )
        self.exportType(OpenMaya.MFn.kFluid, PBRTVolume.Volume.VolumeFactory, "Volume", self.volumeFileHandle)

        if self.meshLocalFileHandle:
            self.meshLocalFileHandle.close()
        if self.meshSyntheticFileHandle:
            self.meshSyntheticFileHandle.close()
        if self.areaLightsFileHandle:
            areaLightsWereWritten = self.areaLightsFileHandle.tell() 
            self.areaLightsFileHandle.close()
        if self.volumeFileHandle:
            self.volumeFileHandle.close()

        #includeFileList.append(self.meshLocalFileHandle)
        includeFileList.append(self.syntheticFileName)
        includeFileList.append(self.areaLightsFileName)
        includeFileList.append(self.volumeFileName)
        
        # MATERIALS        
        if cmds.getAttr( 'pbrt_settings.scene_export_materials' ) == 1:
            self.exportType( OpenMaya.MFn.kDependencyNode, PBRTMaterial.Material.MaterialFactory, "Material" )
                            
        
        # loop though lights
        if cmds.getAttr( 'pbrt_settings.scene_export_lights' ) == 1:
            exportedLights = self.exportType( OpenMaya.MFn.kLight, PBRTLight.Light.LightFactory, "Light" ) 
            if 0==exportedLights \
            and cmds.getAttr( 'pbrt_settings.scene_export_defaultLighting' ) == 1 \
            and areaLightsWereWritten==0:
                self.sceneFileHandle.write( PBRTLight.Light.defaultLighting())
        
        self.exportType( OpenMaya.MFn.kLocator, PBRTLocator.Locator.Factory, "Locator" )

        # WRITE INCLUDES IF EXTERNAL FILES EXIST
        if os.path.exists(self.localFileName):
            self.sceneFileHandle.write('Include "' + self.localFileName + '"' + os.linesep)

        self.sceneFileHandle.write('SyntheticSceneBegin' + os.linesep)
        for includeFile in includeFileList:
            if os.path.exists(includeFile):
                self.sceneFileHandle.write('\tInclude "' + includeFile + '"' + os.linesep)
        self.sceneFileHandle.write('SyntheticSceneEnd' + os.linesep)
        self.sceneFileHandle.write(os.linesep)
        
        
        # finish off the file
        self.log("Closing files")
        
        if not self.debug:
            self.sceneFileHandle.write( os.linesep + 'WorldEnd' )
            self.sceneFileHandle.close()
            
        self.log("Export complete")
        self.dprint("File written: %s"%self.sceneFileName)
         
    
    def findRenderCamera(self):
        cameraItDag = OpenMaya.MItDag(OpenMaya.MItDag.kDepthFirst, OpenMaya.MFn.kCamera)
        
        while not cameraItDag.isDone():
            cameraItDag.getPath(self.tempDagPath)
            currCamName = OpenMaya.MFnDagNode(self.tempDagPath.transform()).partialPathName()
            if ((currCamName == self.renderCameraName) or (self.renderCameraName == self.tempDagPath.partialPathName())):
                return self.tempDagPath
            cameraItDag.next()
        
        return 0
        

    def exportType(self, objType, objModule, logType, theFileHandle = "_undefined"):
        """
        Here we iterate over the specified object type, calling the specified
        export module to handle it, and do the output :)
        Shame we need a different iterator for materials, and some other objects.
        """
        
        if theFileHandle == "_undefined":
            theFileHandle = self.sceneFileHandle
        self.log("Exporting " + logType + " objects...")
        itDn = 0
        isDag = False
        if objType==OpenMaya.MFn.kDependencyNode:
            #create Dg iterator
            itDn = OpenMaya.MItDependencyNodes( OpenMaya.MFn.kDependencyNode )
        else:
            #create Dag iterator
            itDn = OpenMaya.MItDag(OpenMaya.MItDag.kDepthFirst, objType )
            isDag = True
        #self.mComputation.beginComputation()
        exported = 0
            
        while not itDn.isDone():
            #if self.mComputation.isInterruptRequested(): break
            if self.mProgress.isCancelled(): break
            nodeName = ''
            
            expModule = False
            if isDag:
                itDn.getPath(self.tempDagPath)
                theNode = OpenMaya.MFnDagNode(self.tempDagPath)
                nodeName = theNode.name()
                if self.isVisible(theNode):
                    expModule = objModule(theFileHandle, self.tempDagPath)
            else:
                theNode = OpenMaya.MFnDependencyNode( itDn.thisNode() )
                nodeName = theNode.name()
                expModule = objModule(theFileHandle, theNode)
            if expModule !=False:
                expOut = expModule.loadModule()
                self.dprint( "Found "+logType+": "+nodeName )
                self.dprint( expOut ,2)
                self.dprint( "------------",2 )
                exported += 1
                #if not self.debug:
                #    expModule.writeTo( theFileHandle )
            itDn.next()
        self.log("...done")
        return exported
    
    
    def log(self, string):
        """
        Update the progress window with info about what the process is doing.
        """
        
        self.mProgress.setProgressStatus(string)
    
        
    def isVisible(self, fnDag):
        """
        Detect if the given fnDag is visible. (Also checks fnDag's parents.)
        """
        visible = True
        
        if fnDag.isIntermediateObject():
            visible = False
        
        try:
            visPlug = fnDag.findPlug("visibility")
            visible = visPlug.asBool()
        except:
            OpenMaya.MGlobal.displayError("MPlug.asBool")
            visible = False
        
        try:
            dOPlug = fnDag.findPlug("drawOverride")
            
            # ignore object is in template or reference layer
            normalDisplayPlug = dOPlug.child(0)
            if normalDisplayPlug.asInt() != 0:
                visible = False
            
            # ignore object if later is not visible
            layerVisiblePlug = dOPlug.child(6)
            if layerVisiblePlug.asInt() == 0:
                visible = False
        except:
            pass # this is an optional override, so forget about it if it doesn't exist
        
        parentCount = fnDag.parentCount()
        if parentCount > 0 and visible:
            visible = self.isVisible( OpenMaya.MFnDagNode(fnDag.parent(0)) )
        
        return visible
    
    def dprint(self, string, verbosity=1):
        if verbosity <= self.verbosity:
            prefix = 'Info: '
            if verbosity>1:
                prefix = 'DEBUG: '
            OpenMaya.MGlobal.displayInfo(prefix + str(string) )
