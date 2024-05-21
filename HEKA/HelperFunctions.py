from SeriesClass import Series
from SweepClass import Sweep
from TraceClass import Trace

def get_class( obj):
    '''Returns enum class type for object'''
    obj_class = type( obj)

    if obj_class == heka_reader.SeriesRecord:
        return SeriesClass.Series

    if obj_class == heka_reader.SweepRecord:
        return Sweep

    if obj_class == heka_reader.TraceRecord:
        return Trace
