from NogaretClass import Nogaret
from PulseFamilyClass import PulseFamily
from PulseFamilyLeakSubClass import PulseFamilyLeakSub
from PairedPulseFamilyClass import PairedPulseFamily
from PulseFamilyInactivationClass import PulseFamilyInactivation
from SlowInactivationFamilyClass import SlowInactivationFamily
from RampClass import Ramp
from RampBothClass import RampBoth
from GapJunctionPulseFamilyClass import GapJunctionPulseFamily
from GapFreeRecordClass import GapFreeRecord
from GapFreeBothClass import GapFreeBoth
from GapFreeClass import GapFree
from StepRampClass import StepRamp
from TailPulseFamilyClass import TailPulseFamily
from PulseFamilyDynamicClampClass import PulseFamilyDynamicClamp
from PulseClass import Pulse
from OrnsteinUhlenbeckClass import OrnsteinUhlenbeck
from OptoBlueStimClass import OptoBlueStim
from RepeatPulseDynamicClampClass import RepeatPulseDynamicClamp

# Assigning class objects to named protocols
protocols = { 'Nogaret'                : Nogaret,
              'PulseFamily'            : PulseFamily,
              'PulseFamilyLeakSub'     : PulseFamilyLeakSub,
              'Ramp'                   : Ramp,
              'RampBoth'               : RampBoth,
              'Pulse'                  : Pulse,
              'PairedPulseFamily'      : PairedPulseFamily,
              'PulseFamilyInactivation': PulseFamilyInactivation,
              'PulseFamilyDynamicClamp': PulseFamilyDynamicClamp,
              'SlowInactivationFamily' : SlowInactivationFamily,
              'GapJunctionPulseFamily' : GapJunctionPulseFamily,
              'GapFreeRecord'          : GapFreeRecord,
              'GapFree'                : GapFree,
              'GapFreeBoth'            : GapFreeBoth,
              'StepRamp'               : StepRamp,
              'TailPulseFamily'        : TailPulseFamily,
              'OrnsteinUhlenbeck'      : OrnsteinUhlenbeck,
              'OptoBlueStim'           : OptoBlueStim,
              'RepeatPulseDynamicClamp': RepeatPulseDynamicClamp}

# List of protocols to not include in analysis
excluded_protocols = [ 'SealTestKyle',
                       'Breakin' ]
