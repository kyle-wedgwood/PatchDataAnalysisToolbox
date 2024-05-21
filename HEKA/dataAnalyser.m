% Load and analyse data from Patchmaster .dat file
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

function [collated_data,derived_var,user_include_list] = dataAnalyser( filename, experiment_name, include_list)

  close all;
  
  addpath( genpath( '~/Dropbox/Fellowship/Data/PatchDataAnalysisToolbox/'));

  data = HEKA_Importer( filename);
  dataTree = data.trees.dataTree;
  stimTree = data.trees.stimTree;

  recTable = data.RecTable;

  no_entries = size( recTable, 1);
  
  if nargin < 3
    check_flag = true;
    if exist( sprintf( 'include_list_%s.txt', filename), 'file')
      include_list = load( sprintf( 'include_list_%s.txt', filename));
      check_flag = false;
    else
      include_list = 1:no_entries;
    end
  else
    check_flag = false;
  end

  % Need to first figure out where nodes are on data and stim trees
  [dataTreeIndex,stimTreeIndex] = findTreeIndices( dataTree, stimTree, no_entries);

  temp_name = strsplit( filename, '.');
  folder_name = temp_name{1};

  if exist( folder_name, 'dir')
    rmdir( folder_name, 's');
  end
  
  mkdir( folder_name);
  
  % Create output variable
  collated_data = [];
  derived_var   = [];
  
  user_include_list = [];

  for recording_no = include_list
    raw_data  = recTable.dataRaw{recording_no};
    stim_data = recTable.stimWave{recording_no};

    response_unit = recTable.ChUnit{recording_no};
    holding_value = recTable.Vhold{recording_no}{1}(1); % Note that Axon amplifier does not have holding value set in software
    sample_rate   = recTable.SR(recording_no);

    stimulus_name = recTable.Stimulus{recording_no};
    series_count = 0;
    
    switch stimulus_name
      case 'GJSteps'
        [fig,stim_amp,gj_current,conductance] = computeGapJunctionCurrent( raw_data, stim_data, sample_rate, holding_value);
        
        if check_flag
          str = input( 'Add to collated data?', 's');
          if ( isempty( str)) || strcmp( str, 'y')
            collated_data = collateData( collated_data, stim_amp, gj_current);
            derived_var   = [ derived_var; conductance];
            user_include_list(end+1) = recording_no;
          end
        else
          collated_data = collateData( collated_data, stim_amp, gj_current);
          derived_var   = [ derived_var; conductance];
        end
        
    end

    fig_filename = sprintf( '%s/series_%d_%s_%s.png', folder_name, ...
      recording_no-1, stimulus_name, 'analysed_data');

    if exist( 'fig', 'var')
      saveas( fig, fig_filename);
      close( fig);
      clear fig;
    end

  end
  
  fprintf( 'Number of series analysed: %d\n', length( dir( folder_name))-2);
  
  fig = plotCollatedData( collated_data, 'Transjunctional potential (mv)', 'Current (pA)', experiment_name);
  save_fig( fig, folder_name, experiment_name, 'gj_current');
  
  fig = makeBoxplot( mean( derived_var, 2), 'Conductance (nS)', {experiment_name});
  save_fig( fig, folder_name, experiment_name, 'gj_conductance');
  
  if check_flag
    save( sprintf( 'include_list_%s.txt', filename), 'user_include_list', '-ascii');
  end
  
  conductance = derived_var;
  save( sprintf( '%s_analysed_data.mat', filename), 'collated_data', 'conductance');

end

function collatedData = collateData( collatedData, stimData, responseData)

  if isempty( collatedData)
    for response_no = 1:size( stimData, 1)
      collatedData(response_no).stim     = stimData(response_no);
      collatedData(response_no).response = responseData(response_no,:);
    end
  else
    for response_no = 1:size( stimData, 1)
      ind = find( abs( stimData(response_no) - vertcat( collatedData.stim, [])) < 0.001);
      if ~isempty( ind)
        collatedData(ind).response = [ collatedData(ind).response; responseData(response_no,:)];
      else
        collatedData(end+1).stim   = stimData(response_no);
        collatedData(end).response = responseData(response_no,:);
      end
    end
  end
end

function [dataTreeIndex,stimTreeIndex] = findTreeIndices( dataTree, stimTree, no_entries)

  dataTreeIndex = zeros( no_entries, 1);
  stimTreeIndex = zeros( no_entries, 1);

  dataIndex = 1;
  stimIndex = 1;

  dataTreeLength = size( dataTree, 1);
  stimTreeLength = size( stimTree, 1);

  for i = 1:no_entries
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

function fig = plotCollatedData( collatedData, x_label, y_label, label)

  fig = figure( 'Position', [0,0,1200,800]);
  ax = axes( fig); hold on;
  
  x_data = vertcat( collatedData.stim, []);
  y_data = zeros( size( x_data));
  std_data = zeros( size( y_data));
  sem_data = zeros( size( y_data));
  
  for response_no = 1:length( collatedData)
    y_data(response_no,:)   = mean( collatedData(response_no).response(:), 1);
    std_data(response_no,:) = std( collatedData(response_no).response(:));
    sem_data(response_no,:)  = std_data( response_no)/sqrt( size( collatedData(response_no).response, 1));
  end
  
  h = plot( ax, x_data, y_data, 'Linewidth', 4.0);
  color = get( h, 'Color');
  errorbar( ax, x_data, y_data, sem_data, 'Color', color,  'Linewidth', 2.0);
  
  x_lim = get( gca, 'XLim');
  line( [x_lim(1),x_lim(2)], [0,0], 'Linewidth', 4.0, 'Linestyle', ':', 'Color', 0.5*ones(1,3));
  
  xlabel( x_label);
  ylabel( y_label);
  title( label);
  
  text( ax, x_data(end), max( y_data(:)), sprintf( 'N = %d', size( collatedData( response_no).response, 1)), ...
    'Fontsize', 20.0);
  
  set( gca, 'Fontsize', 20);
  
end

function fig = makeBoxplot( data, y_label, x_tick_label)

  fig = figure( 'Position', [0,0,1200,800]);
  ax = axes( fig); hold on;
    
  boxplot( ax, data);
  
  ylabel( y_label);

  set( gca, 'XTickLabel', x_tick_label);
  set( gca, 'Fontsize', 20);
  
  % Run t-tests
  [~,p_val] = ttest( data);
  fprintf( 'P value one sample test (zero mean): %f\n', p_val);
  
  text( ax, 0.8, mean( data), sprintf( 'N = %d', size( data, 1)), 'Fontsize', 20.0);
  
  if p_val < 0.05
    text( ax, 1.2, mean( data), sprintf( '* p = %f', p_val), 'Fontsize', 20.0);
  end
  
end

function save_fig( fig, folder_name, experiment_name, string)
  fig_filename = sprintf( '%s/%s_%s.png', folder_name, ...
      experiment_name, string);
  saveas( fig, fig_filename);
  close( fig);
end