# ------------------------------------------------------------------------------
# PBRT exporter python script plugin for Maya
#
# This file is licensed under the GPL
# http://www.gnu.org/licenses/gpl-3.0.txt
#
# $Id$
#
# ------------------------------------------------------------------------------
#
# Code that generates commands for various render settings: filtering, sampling, integration, etc.
#
# ------------------------------------------------------------------------------


# uncomment for ability to update the module without restarting Maya
# import ExportModule
# reload(ExportModule)
from ExportModule import ExportModule

from maya import cmds

class RenderGlobals(ExportModule):
    """
    Settings ExportModule. Responsible for getting the scene's render settings.
    """
    
    def __init__(self, nWidth, nHeight, nImageName):
        """
        Constructor. Set's up this object with required data.
        """
        
        self.width = nWidth
        self.height = nHeight
        self.imageName = nImageName
        self.getOutput()
        
    def outputBool(self,attribute,prefix=''):
        self.addToOutput( '\t"bool %s" ["%s"]' % (attribute, str(cmds.getAttr( 'pbrt_settings.'+prefix+attribute)).lower() ) )

    def outputFloat(self,attribute,prefix=''):
        self.addToOutput( '\t"float %s" [%f]' % (attribute, cmds.getAttr( 'pbrt_settings.'+ prefix+attribute)  ))

    def outputInt(self,attribute,prefix=''):
        self.addToOutput( '\t"integer %s" [%d]' % (attribute, cmds.getAttr( 'pbrt_settings.'+ prefix+attribute) ) )

    def outputEnum(self,attribute,prefix=''):
        self.addToOutput( '\t"string %s" ["%s"]' % (attribute, cmds.getAttr( 'pbrt_settings.'+prefix+attribute, asString = True).lower() ) )

        
    def getOutput(self):
        """
        Append this module's output to the scene file buffer.
        """
        self.doFilm()
        self.doSamlpler()
        #self.doRenderer()
        self.doIntegrator()
        self.doVolumeIntegrator()
        self.doAccelerator()
        
        extraText = cmds.getAttr('pbrt_settings.extra_commands')
        if extraText:
            self.addToOutput(extraText)
        self.addToOutput('')     

        
    def doFilm(self):
        """
        Export Film settings
        """
        self.addToOutput( 'Film "image"' )
        self.addToOutput( '\t"integer xresolution" [%i]' % self.width )
        self.addToOutput( '\t"integer yresolution" [%i]' % self.height )
        self.addToOutput( '\t"string filename" ["%s"]' % self.imageName )
        self.addToOutput( '' )


    def doSamlpler(self):
        """
        Export Sampling settings
        """

        self.addToOutput('Sampler "bestcandidate"')
        self.addToOutput( '' )
            
            
    def doPixelFilter(self):
        """
        Export Filter settings
        """
        
        pixel_filter        = cmds.getAttr( 'pbrt_settings.pixel_filter', asString = True ).lower()
        pixel_filter_xwidth = cmds.getAttr( 'pbrt_settings.pixel_filter_xwidth' )
        pixel_filter_ywidth = cmds.getAttr( 'pbrt_settings.pixel_filter_ywidth' )
        pixel_filter_b      = cmds.getAttr( 'pbrt_settings.pixel_filter_b' )
        pixel_filter_c      = cmds.getAttr( 'pbrt_settings.pixel_filter_c' )
        pixel_filter_alpha  = cmds.getAttr( 'pbrt_settings.pixel_filter_alpha' )
        pixel_filter_tau    = cmds.getAttr( 'pbrt_settings.pixel_filter_tau' )
        
        self.addToOutput( 'PixelFilter "%s"' % pixel_filter )
        self.addToOutput( '\t"float xwidth" [%f]' % pixel_filter_xwidth )
        self.addToOutput( '\t"float ywidth" [%f]' % pixel_filter_ywidth )
        
        if pixel_filter == "mitchell":
            self.addToOutput( '\t"float B" [%f]' % pixel_filter_b )
            self.addToOutput( '\t"float C" [%f]' % pixel_filter_c )
        
        if pixel_filter == "gaussian":
            self.addToOutput( '\t"float alpha" [%f]' % pixel_filter_alpha )
            
        if pixel_filter == "sinc":
            self.addToOutput( '\t"float tau" [%f]' % pixel_filter_tau )
            
        self.addToOutput( '' )      
        

        
    def doRenderer(self):
        """
        Export Renderer settings: Sampler, Metropolis, etc.
        """
        
        renderer        = cmds.getAttr( 'pbrt_settings.renderer', asString = True ).lower()
        self.addToOutput( 'Renderer "%s"' % renderer )
        if renderer== 'sampler':
            self.outputBool('visualizeobjectids')
        elif renderer== 'metropolis':
            self.outputFloat('largestepprobability')
            self.outputInt('samplesperpixel')
            self.outputInt('bootstrapsamples')
            self.outputInt('directsamples')
            self.outputBool('dodirectseparately')
            self.outputInt('maxconsecutiverejects')
            self.outputInt('maxdepth')
            self.outputBool('bidirectional')
        
        self.addToOutput( '' )      
        
    def doIntegrator(self):
        """
        Export Integrator settings
        """
        self.addToOutput('SurfaceIntegrator "dipolesubsurface"')
        self.addToOutput('\t"float minsampledistance"[.1]')
        self.addToOutput('\t"float maxerror"[.05]')
        self.addToOutput('\t"float scale"[7]')
        self.addToOutput( '' )


    def doVolumeIntegrator(self):
        """
        Export Volume Integrator Settings
        """
        self.addToOutput('VolumeIntegrator "single" "float stepsize" [.2]')
        self.addToOutput( '' )

        
    def doAccelerator(self):   
        """
        Export Acclelerator settings. Not sure if someone will change the defaults, which should be pretty good for most cases
        """   
        accelerator        = cmds.getAttr( 'pbrt_settings.accelerator', asString = True ).lower()
        self.addToOutput( 'Accelerator "%s"' % accelerator )
        if accelerator== 'bvh':
            self.outputInt('maxnodeprims','accelerator_')
        elif accelerator== 'grid':
            self.outputEnum('splitmethod','accelerator_')
            self.outputBool('refineimmediately','accelerator_')
        elif accelerator== 'kdtree':
            self.outputInt('intersectcost','accelerator_')
            self.outputInt('traversalcost','accelerator_')
            self.outputFloat('emptybonus','accelerator_')
            self.outputInt('maxprims','accelerator_')
            self.outputInt('maxdepth','accelerator_')
        self.addToOutput( '' )
            
            