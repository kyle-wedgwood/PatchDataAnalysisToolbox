import os
import shutil
import heka_reader
from BaseClass import Base

class Experiment( Base):
    '''Class to store data for whole recording session'''

    def __init__( self, filename):
        '''Initialiser for experiment class'''

        self.filename = filename
        self.foldername = filename.split('.')[0]
        self.load_notes()

        bundle = heka_reader.Bundle( filename)
        self.data = bundle.data
        self.start_time = self.convert_time( bundle.pul.StartTime)

        super( Experiment, self).__init__( None, bundle.pul[0], 0)


    def make_pdf_report( self):
        '''Produces a PDF report with notes and data plotted'''

        # self.create_matlab_figures()

        from fpdf import FPDF
        pdf = FPDF()
        pdf.line_height = 5
        pdf.line_width  = 40
        pdf.set_top_margin( 10.0)
        pdf.set_left_margin( 10.0)
        pdf.add_page()

        super( Experiment, self).make_pdf_report( pdf)
        filename = self.filename + '_report.pdf'
        pdf.output( filename, 'F')

        shutil.rmtree( self.foldername)

        print( 'PDF report successfully generated')


    def create_matlab_figures( self):
        '''Creates a dummy matlab script to create figures'''
        fid = open( 'create_matlab_figures.m', 'w')

        fid.write( "addpath( genpath( '~/Dropbox/Fellowship/Data/PatchDataAnalysisToolbox/'));")
        fid.write( "dataPlotter( '%s')" % self.filename)

        fid.close()

        command = '/Applications/MATLAB_R2017b.app/bin/matlab -nodesktop -nodisplay -r "create_matlab_figures"'

        os.system( command)

        os.remove( 'create_matlab_figures.m')
