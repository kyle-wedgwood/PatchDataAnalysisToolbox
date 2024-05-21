function fig = plotGJSteps( rawData, stimData, sampleRate, holdingValue)
    
    V_scale = 1e3;
    I_scale = 1e12;

    no_channels = size( rawData, 2);
    no_sweeps = size( rawData{1}, 2);
    npts = size( rawData{1}, 1);
    dt = 1.0/sampleRate;
    
    time = (0:npts-1)*dt*1000;
    
    stim_names  = fieldnames( stimData);
    c_map_names = {'Blues6','Oranges6'};
    
    % Scale data to mV and pA
    for channel_no = 1:no_channels
      rawData{channel_no} = rawData{channel_no}*I_scale;
      stimData.(stim_names{channel_no}) = (stimData.(stim_names{channel_no})+holdingValue)*V_scale;
    end
    
    % Make stimulus figure
    fig = figure( 'Position', [0,0,1200,400]);

    % Make response figure
    ax1 = subplot( 1, 2, 1); hold on;
    ax2 = subplot( 1, 2, 2); hold on;
    for channel_no = 1:no_channels
      c_map{channel_no} = othercolor( c_map_names{channel_no}, no_sweeps+1);
      for sweep_no = 1:no_sweeps
        stimLine(sweep_no,channel_no) = plot( ax1, time, stimData.(stim_names{channel_no})(:,sweep_no), ...
          'Linewidth', 2.0, 'Color', c_map{channel_no}(sweep_no+1,:));
        dataLine(sweep_no,channel_no) = plot( ax2, time, rawData{channel_no}(:,sweep_no), ...
          'Linewidth', 2.0, 'Color', c_map{channel_no}(sweep_no+1,:));
      end
    end
    
    xlim( ax1, [time(1),time(end)]);
    xlim( ax2, [time(1),time(end)]);
    
    % Add labels
    xlabel( ax1, 'Time (ms)');
    xlabel( ax2, 'Time (ms)');

    ylabel( ax1, 'Voltage (mV)');
    ylabel( ax2, 'Current (pA)');
    
    set( ax1, 'Fontsize', 20);
    set( ax2, 'Fontsize', 20);
    
end