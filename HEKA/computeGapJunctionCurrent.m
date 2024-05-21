function [fig,stim_amp,gj_current,gj_conductance] = computeGapJunctionCurrent( rawData, stimData, sampleRate, holdingValue)
  % Computes gap junction current (not scaled by membrane capacitance)
  
  V_scale = 1e3;
  I_scale = 1e12;
  
  no_channels = size( rawData, 2);
  no_sweeps = size( rawData{1}, 2);
  npts = size( rawData{1}, 1);
  dt = 1.0/sampleRate;
  
  stim_names  = fieldnames( stimData);
  
  % Scale data to mV and pA
  for channel_no = 1:no_channels
    rawData{channel_no} = rawData{channel_no}*I_scale;
    stimData.(stim_names{channel_no}) = (stimData.(stim_names{channel_no})+holdingValue)*V_scale;
  end
  
  % Find start and end times for stimulus
  start_ind = cell( 2, 1);
  stop_ind  = cell( 2, 1);
  
  for channel_no = 1:no_channels
    D = diff( stimData.( stim_names{channel_no}));
    ind = find( D);
    start_ind{channel_no} = ind(1)+1;
    stop_ind{channel_no}  = ind(2);
  end
  
  % Create struct to store output
  gj_current = zeros( size( rawData{1}, 2), no_channels);
  gj_conductance = zeros( 1, no_channels);
  
  base_ind = 1:min( cell2mat( start_ind))-1;

  % Do analysis
  for channel_no = 1:no_channels
    alt_channel_no = mod( channel_no, 2) + 1;
    test_ind = 0.5*( start_ind{channel_no} + stop_ind{channel_no}-1):stop_ind{channel_no}-1;
    stim_amp = mean( stimData.( stim_names{channel_no})(test_ind,:));
    stim_amp = (stim_amp - holdingValue*V_scale)';
    base_response = mean( rawData{alt_channel_no}(base_ind,:))';
    mean_response = mean( rawData{alt_channel_no}(test_ind,:))' - base_response;
    gj_current(:,channel_no) = mean_response;
    gj_conductance(:,channel_no) = compute_conductance( stim_amp, mean_response);
  end
  
  % Plot results
  fig = figure;
  
  h = plot( stim_amp, gj_current, 'Linewidth', 4.0);
  line( [stim_amp(1),stim_amp(end)],[0,0], 'Linestyle', ':', 'Color', 0.5*ones( 1, 3), 'Linewidth', 4.0);
  xlabel( 'Transjunctional potential (mV)');
  ylabel( 'Current (pA)');
  set( gca, 'Fontsize', 20.0);

end

function conductance = compute_conductance( stim_amp, current)
  
  ind = (stim_amp <= 100.0);
  X = [ ones( size( stim_amp(ind))), stim_amp(ind)];
  beta = X\current(ind);
  conductance = -beta(2);
  
end