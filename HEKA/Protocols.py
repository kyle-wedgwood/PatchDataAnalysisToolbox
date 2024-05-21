from ContinuousClass import Continuous
from ContinuousVoltageClass import ContinuousVoltage
from VC_AxonClass import VC_Axon
from CCAxonClass import CCAxon
from CCBothClass import CCBoth
from RampClass import Ramp
from BothRampClass import BothRamp
from GJStepsClass import GJSteps
from GJOnePulseClass import GJOnePulse
from VCICClass import VCIC
from IVStepsClass import IVSteps

# Assinging class objects to named protocols
protocols = { 'Continuous': Continuous,
              'ContinuousVoltage': ContinuousVoltage,
              'VC_Axon'   : VC_Axon,
              'CCAxon'    : CCAxon,
              'CCBoth'    : CCBoth,
              'Ramp'      : Ramp,
              'BothRamp'  : BothRamp,
              'GJSteps'   : GJOnePulse,
              'GapJunction': GJSteps,
              'GJSimulPulse': GJOnePulse,
              'GJOnePulse': GJOnePulse,
              'VC-IC'     : VCIC,
              'I-Vsteps'  : IVSteps,
              'IV'        : IVSteps
        }

# List of protocols to not include in analysis
excluded_protocols = []

