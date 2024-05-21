% Load and plot data from Patchmaster .dat file
% Uses HEKA_Importer from Christian Keine
% (https://uk.mathworks.com/matlabcentral/fileexchange/70164-heka-patchmaster-importer)

% % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % %
% Note on data format:
%
% RecTable contains acquisition parameters, including stimulus name, raw data
% and actual stimulus in the (row) order that they were collected.
%
% Trees contains a nested structure (how Patchmaster saves its objects) for
% data, stimuli and solutions. Note that I did not use the solutions option
% when making recordings, but all solutions were the same as in the notes.
%
% The order of the dataTree is Root -> Group -> Series -> Sweep -> Trace,
% with appropriate settings stored at each level. Note that the trace tells
% you which channel was actually recorded from. Also note that I never used
% the Group setting, so we only need pay attention from Series onwards.
%
% The name of the protocol can be founds in the seLabel field of the Series
% object. These are to be matched with the headings in the stimTree object.
%
% The order of the stimTree is Root -> Stimulation -> Channel -> Segment.
% Essentially, the StimulationRecord is the top-level for each
% protocol. The order of the stimuli in the tree is the same as the data
% acquisition in the RecTable and the dataTree (so that EACH recording) has
% its own entry in the stimTree.
%
% The name of the protocol is listed in the stEntryName of the Stimulation
% node. The holding value (where appropriate) is found in the chHolding
% field on the Channel node. The segments are listed in the order in which
% they appear in the actual protocol
%
% i.e. pre_stim_seg -> step_seg -> tail_seg
%
% There are various options that are saved as enumerated flags, i.e.
% seSegmentClass (0 - Constant, 1 - Ramp, 2 - Continuous, etc.) and
% chAmplModel (0 - Any, 1 - VClamp, 2 - CClamp). See the stimFile_v10000.txt
% text document for further details.
%
% For some reason, loading of Ramp segments seems to be broken (loader
% interprets them as constant segments). They should be a ramp from the
% previous seVoltage value to the segment seVoltage over the seDuration
% specified.
%
% Kyle Wedgwood
% 4.8.2019

function data = dataPlotter( filename)

  addpath( genpath( '~/Dropbox/Fellowship/Data/PatchDataAnalysisToolbox/'));

  data = HEKA_Importer( filename);
  dataTree = data.trees.dataTree;
  stimTree = data.trees.stimTree;

  recTable = data.RecTable;

  noEntries = size( recTable, 1);

  % Need to first figure out where nodes are on data and stim trees
  [dataTreeIndex,stimTreeIndex] = findTreeIndices( dataTree, stimTree, noEntries);

  temp_name = strsplit( filename, '.');
  folder_name = temp_name{1};

  if ~exist( folder_name, 'dir')
    mkdir( folder_name);
  end

  for recording_no = 1:noEntries
    disp( recording_no)
    raw_data  = recTable.dataRaw{recording_no};
    stim_data = recTable.stimWave{recording_no};

    response_unit = recTable.ChUnit{recording_no};
    holding_value = recTable.Vhold{recording_no}{1}(1); % Note that Axon amplifier does not have holding value set in software
    sample_rate   = recTable.SR(recording_no);

    stimulus_name = recTable.Stimulus{recording_no};

    switch stimulus_name
      case 'Ramp'
        fig = plotRamp( raw_data, stimTree, stimTreeIndex(recording_no), sample_rate, holding_value);
      case 'BothRamp'
        fig = plotBothRamp( raw_data, stimTree, stimTreeIndex(recording_no), sample_rate, holding_value);
      case 'GJSteps'
        fig = plotGJSteps( raw_data, stim_data, sample_rate, holding_value);
      case 'GJOnePulse'
        fig = plotGJOnePulse( raw_data, stim_data, sample_rate, holding_value);
      case 'GJSimulPulse'
        fig = plotGJSimulPulse( raw_data, stim_data, sample_rate, holding_value);
      case 'GapJunction'
        fig = plotGJSimulPulse( raw_data, stim_data, sample_rate, holding_value);
      case 'I-Vsteps'
        fig = plotIVSteps( raw_data, sample_rate);
      case 'IV'
        fig = plotIVSteps( raw_data, sample_rate);
%       case 'CCBoth'
%         fig = plotContinuous( raw_data, sample_rate);
      case 'CCAxon'
        fig = plotContinuous( raw_data, sample_rate);
      case 'Continuous'
        fig = plotContinuous( raw_data, sample_rate);
      %case 'ContinuousVoltage'
        %fig = plotContinuousVoltage( raw_data, sample_rate);
      %case 'VC_Axon'
        %fig = plotContinuousVoltage( raw_data, sample_rate);
      case 'VC-IC'
        fig = plotVCICSteps( raw_data, sample_rate, response_unit);

    end

    fig_filename = sprintf( '%s/series_%d_%s_%s.png', folder_name, ...
      recording_no-1, stimulus_name, 'stimulus_response');

    if exist( 'fig', 'var')
      saveas( fig, fig_filename);
      close( fig);
      clear fig;
    end

  end

  fprintf( 'Number of series in file: %d\n', size( data.RecTable, 1));
  fprintf( 'Number of plots produced: %d\n', length( dir( folder_name))-2);

end

function [dataTreeIndex,stimTreeIndex] = findTreeIndices( dataTree, stimTree, noEntries)

  dataTreeIndex = zeros( noEntries, 1);
  stimTreeIndex = zeros( noEntries, 1);

  dataIndex = 1;
  stimIndex = 1;

  dataTreeLength = size( dataTree, 1);
  stimTreeLength = size( stimTree, 1);

  for i = 1:noEntries
    for index = dataIndex+1:dataTreeLength
      if ~isempty( dataTree{index,3})
        dataIndex = index;
        break
      end
    end
    dataTreeIndex(i) = dataIndex;
    for index = stimIndex+1:stimTreeLength
      if ~isempty( stimTree{index,2})
        stimIndex = index;
        break
      end
    end
    stimTreeIndex(i) = stimIndex;
  end

end
