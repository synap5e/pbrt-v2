
from maya import OpenMaya
from maya import OpenMayaFX

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

        # Store resolution (Taken from https://groups.google.com/forum/#!topic/python_inside_maya/J8nGLgOQp3U)
        xRes_p = OpenMaya.MScriptUtil().asUintPtr()
        yRes_p = OpenMaya.MScriptUtil().asUintPtr()
        zRes_p = OpenMaya.MScriptUtil().asUintPtr()
        self.fFluid.getResolution(xRes_p, yRes_p, zRes_p)
        xRes = OpenMaya.MScriptUtil().getUint(xRes_p)
        yRes = OpenMaya.MScriptUtil().getUint(yRes_p)
        zRes = OpenMaya.MScriptUtil().getUint(zRes_p)
        self.resolution = (xRes, yRes, zRes)

        # Bounding Box
        bounding_box = self.fFluid.boundingBox()
        self.pointMin = bounding_box.min()
        self.pointMax = bounding_box.max()

        # Density values
        fluidDensity = self.fFluid.density()

        self.density = []
        for z in range(0, zRes):
            for y in range(0, yRes):
                for x in range(0, xRes):
                    value = self.fFluid.index(x, y, z)
                    self.density.append(OpenMaya.MScriptUtil.getFloatArrayItem(fluidDensity, value))


    @staticmethod
    def VolumeFactory(fileHandle, dagPath):
        OpenMaya.MGlobal.displayInfo("In Volume Factory")
        volumeExporter = Volume(fileHandle, dagPath)
        return volumeExporter

    def getOutput(self):
        OpenMaya.MGlobal.displayInfo("In Volume GetOutput")
        self.addToOutput('# Volume %s' % (self.dagPath.fullPathName()))
        self.getVolume()
        self.addToOutput('')
        self.fileHandle.flush()


    def getVolume(self):
        OpenMaya.MGlobal.displayInfo("In Volume GetGeometry")
        self.addToOutput('\tTransformBegin')
        self.addToOutput( self.translationMatrix( self.dagPath ) )
        self.addToOutput('\tVolume "volumegrid"')
        self.addToOutput('\t"integer nx" [%i] "integer ny" [%i] "integer nz" [%i]' % (self.resolution[0], self.resolution[1], self.resolution[2]))
        self.addToOutput('\t"point p0" [%f %f  %f]' % (self.pointMin.x, self.pointMin.y, self.pointMin.z))
        self.addToOutput('\t"point p1" [%f %f  %f]' % (self.pointMax.x, self.pointMax.y, self.pointMax.z))


        self.addToOutput('\t"float density" [')
        self.addToOutput('\t\t' + ' '.join("%.6f" % x for x in self.density))
        self.addToOutput('\t]')

        self.addToOutput('\t"color sigma_a" [%f %f  %f]' % (1, 1, 0.7))
        self.addToOutput('\t"color sigma_s" [%f %f  %f]' % (2.5, 2.5, 1.5))
        self.addToOutput('\t"color Le" [%f %f  %f]' % (2.5, 2.5, 1))
        self.addToOutput('\tTransformEnd')