function fig = plotBothRamp( rawData, stimTree, stimIndex, sampleRate, holdingValue)
    
    V_scale = 1e3;
    I_scale = 1e12;

    no_channels = size( rawData, 2);
    no_sweeps = 1;
    npts = size( rawData{1}, 1);
    dt = 1.0/sampleRate;
    
    time = (0:npts-1)*dt*1000;
    c_map_names = {'Blues6','Oranges6'};
    
    % Find start and end points of ramp
    segment_index = stimIndex+2;
    segment = stimTree{segment_index,4};
    value  = [];
    class  = [];
    duration = [];
    
    while ~isempty( segment)
      value  = [value;segment.seVoltage];
      class  = [class;segment.seClass];
      duration = [duration;segment.seDuration];
      segment_index = segment_index+1;
      segment = stimTree{segment_index,4};
    end
    
    % Define stimulus
    start_times = cumsum( duration)*1000;
    stimData = zeros( npts, 1);
    ramp_seg = find( class==1);
    slope = (value(ramp_seg)-value(ramp_seg-1))/(1000*duration(ramp_seg));
    ind = logical( (time>start_times(ramp_seg-1)).*(time<start_times(ramp_seg)));
    stimData(ind) = value(ramp_seg) + slope*(time(ind)'-start_times(ramp_seg));
    stimData = ( stimData+holdingValue)*V_scale;
    
    % Scale data to mV and pA
    for channel_no = 1:no_channels
      rawData{channel_no} = rawData{channel_no}*I_scale;
    end
    
    % Make stimulus figure
    fig = figure( 'Position', [0,0,1200,400]);
    
    % Select correct trace if required
    for channel_no = 1:no_channels
      if size( rawData{channel_no}, 2) > 1
        rawData{channel_no} = rawData{channel_no}(:,channel_no);
      end
    end

    % Make response figure
    ax1 = subplot( 1, 2, 1); hold on;
    ax2 = subplot( 1, 2, 2); hold on;
    for channel_no = 1:no_channels
      c_map{channel_no} = othercolor( c_map_names{channel_no}, no_sweeps+1);
        stimLine(channel_no) = plot( ax1, time, stimData, ...
          'Linewidth', 2.0, 'Color', c_map{channel_no}(2,:));
        try
        dataLine(channel_no) = plot( ax2, time, rawData{channel_no}, ...
          'Linewidth', 2.0, 'Color', c_map{channel_no}(2,:));
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