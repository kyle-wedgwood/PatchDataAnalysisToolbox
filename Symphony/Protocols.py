from BlueGeneralStimClass import BlueGeneralStim
from BluePulseFamilyClass import BluePulseFamily
from BlueStepRampClass import BlueStepRamp
from CBCVoltageClampClass import CBCVoltageClamp
from CBCVoltageClampVaryGLClass import CBCVoltageClampVaryGL
from GapFreeBothClass import GapFreeBoth
from GapFreeClass import GapFree
from GapFreeRecordClass import GapFreeRecord
from GapJunctionPulseFamilyClass import GapJunctionPulseFamily
from NogaretClass import Nogaret
from NogaretFuraHamamatsuClass import NogaretFuraHamamatsu
from OptoBlueStimClass import OptoBlueStim
from OrnsteinUhlenbeckClass import OrnsteinUhlenbeck
from PairedPulseFamilyClass import PairedPulseFamily
from PulseClass import Pulse
from PulseFamilyClass import PulseFamily
from PulseFamilyDynamicClampClass import PulseFamilyDynamicClamp
from PulseFamilyInactivationClass import PulseFamilyInactivation
from PulseFamilyLeakSubClass import PulseFamilyLeakSub
from RampBothClass import RampBoth
from RampClass import Ramp
from RepeatPulseDynamicClampClass import RepeatPulseDynamicClamp
from SlowInactivationFamilyClass import SlowInactivationFamily
from StepRampClass import StepRamp
from TailPulseFamilyClass import TailPulseFamily
from TriangleRampClass import TriangleRamp

# Assigning class objects to named protocols. Can use this to override default analysis method
protocols = { 'BlueGeneralStim'        : BlueGeneralStim,
              'BluePulseFamily'        : BluePulseFamily,
              'BlueStepRamp'           : BlueStepRamp,
              'CBCSteadyState'         : CBCVoltageClamp,
              'CBCVoltageClamp'        : CBCVoltageClamp,
              'CBCVoltageClampVaryGL'  : CBCVoltageClampVaryGL,
              'GapJunctionPulseFamily' : GapJunctionPulseFamily,
              'GapFree'                : GapFree,
              'GapFreeBoth'            : GapFreeBoth,
              'GapFreeRecord'          : GapFreeRecord,
              'Nogaret'                : Nogaret,
              'NogaretFuraHamamatsu'   : NogaretFuraHamamatsu,
              'BluePulseFamily'        : BluePulseFamily,
              'OrnsteinUhlenbeck'      : OrnsteinUhlenbeck,
              'OptoBlueStim'           : OptoBlueStim,
              'PairedPulseFamily'      : PairedPulseFamily,
              'Pulse'                  : Pulse,
              'PulseFamily'            : PulseFamily,
              'PulseFamilyDynamicClamp': PulseFamilyDynamicClamp,
              'PulseFamilyInactivation': PulseFamilyInactivation,
              'PulseFamilyLeakSub'     : PulseFamilyLeakSub,
              'Ramp'                   : Ramp,
              'RampBoth'               : RampBoth,
              'RepeatPulseDynamicClamp': RepeatPulseDynamicClamp,
              'SlowInactivationFamily' : SlowInactivationFamily,
              'StepRamp'               : StepRamp,
              'TailPulseFamily'        : TailPulseFamily,
              'TriangleRamp'           : TriangleRamp}

# List of protocols to not include in analysis
excluded_protocols = [ 'SealTestKyle',
                       'Breakin' ]
