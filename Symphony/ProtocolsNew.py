import glob
import os

folder = os.getcwd()
symphony_folder = '/Users/kcaw201/Dropbox/Fellowship/Data/PatchDataAnalysisToolbox/Symphony'

os.chdir(symphony_folder)

classes = glob.glob('*Class.py')
print(classes)

# Remove the non-protocol classes
classes_to_remove = ['Base', 'Experiment', 'Subject', 'Preparation', 'Cell', 'AbstractProtocol', 'EpochGroup', 'Epoch']

for name in classes_to_remove:
    classes.remove(name + 'Class.py')


# Load the protocol classes + assign class objects to named protocols
protocols = {}
for name in classes:
    root_name = name.split('Class')[0]
    protocols[root_name] = getattr(__import__(root_name + "Class", fromlist=[""]), root_name) 


# List of protocols to not include in analysis
excluded_protocols = [ 'SealTestKyle',
                       'Breakin' ]

os.chdir(folder)