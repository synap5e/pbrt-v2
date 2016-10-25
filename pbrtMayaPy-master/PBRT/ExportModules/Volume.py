
from maya import OpenMaya
from maya import OpenMayaFX
import maya.cmds as cmds

# uncomment for interactive development
# import ExportModule
# reload(ExportModule)
from ExportModule import ExportModule

class Volume(ExportModule):
    fileHandle = int()

    def __init__(self, fileHandle, dagPath):
        self.dagPath = dagPath
        self.fFluid = OpenMayaFX.MFnFluid(dagPath)
        self.fileHandle = fileHandle
        
	# Store resolution 
	self.resolution = cmds.getAttr(self.dagPath.fullPathName() + ".resolution" )
	xRes = int(self.resolution[0][0])
	yRes = int(self.resolution[0][1])
	zRes = int(self.resolution[0][2])

        # Bounding Box
        bounding_box = self.fFluid.boundingBox()
        self.pointMin = bounding_box.min()
        self.pointMax = bounding_box.max()

        # Density values
        self.density = []
        for z in range(0, zRes):
            for y in range(0, yRes):
                for x in range(0, xRes):
                    value = cmds.getFluidAttr(self.dagPath.fullPathName(), at='density', xi=x, yi=y, zi=z)
                    self.density.append(value[0])

        # Color values
        self.color = []
        for z in range(0, zRes):
            for y in range(0, yRes):
                for x in range(0, xRes):
                    value = cmds.getFluidAttr(self.dagPath.fullPathName(), at='color', xi=x, yi=y, zi=z)
                    for c in range(0, 3):
                        self.color.append(value[c])

    @staticmethod
    def VolumeFactory(fileHandle, dagPath):
        volumeExporter = Volume(fileHandle, dagPath)
        return volumeExporter

    def getOutput(self):
        self.addToOutput('# Volume %s' % (self.dagPath.fullPathName()))
        self.getVolume()
        self.addToOutput('')
        self.fileHandle.flush()


    def getVolume(self):
        self.addToOutput('\tTransformBegin')
        self.addToOutput( self.translationMatrix( self.dagPath ) )
        self.addToOutput('\tVolume "volumegrid"')
        self.addToOutput('\t"integer nx" [%i] "integer ny" [%i] "integer nz" [%i]' % (self.resolution[0][0], self.resolution[0][1], self.resolution[0][2]))
        self.addToOutput('\t"point p0" [%f %f  %f]' % (self.pointMin.x, self.pointMin.y, self.pointMin.z))
        self.addToOutput('\t"point p1" [%f %f  %f]' % (self.pointMax.x, self.pointMax.y, self.pointMax.z))


        self.addToOutput('\t"float density" [')
	self.addToOutput('\t\t' + ' '.join("%.6f" % x for x in self.density))
        self.addToOutput('\t]')

        self.addToOutput('\t"float color" [')
        self.addToOutput('\t\t' + ' '.join("%.3f" % x for x in self.color))
        self.addToOutput('\t]')

        self.addToOutput('\t"color sigma_a" [%.1f %.1f  %.1f]' % (1, 0.7, 0.5))
        self.addToOutput('\t"color sigma_s" [%.1f %.1f  %.1f]' % (2, 1.5, 1))
        self.addToOutput('\t"color Le" [%.1f %.1f  %.1f]' % (3, 3, 3))
        self.addToOutput('\tTransformEnd')