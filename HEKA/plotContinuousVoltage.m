function fig = plotContinuousVoltage( rawData, sampleRate)
    
    I_scale = 1e12;

    no_channels = size( rawData, 2);
    npts = size( rawData{1}, 1);
    dt = 1.0/sampleRate;
    
    time = (0:npts-1)*dt*1000;
    
    c_map_names = {'Blues6','Oranges6'};
    
    % Scale data to mV and pA
    for channel_no = 1:no_channels
      rawData{channel_no} = rawData{channel_no}*I_scale;
    end
    
    no_channels = 1;
    
    % Make stimulus figure
    fig = figure( 'Position', [0,0,1200,400]);
    ax = axes( fig);
    hold on;

    % Make response figure
    for channel_no = 1:no_channels
      c_map{channel_no} = othercolor( c_map_names{channel_no}, 2);
        dataLine(channel_no) = plot( ax, time, rawData{channel_no}, ...
          'Linewidth', 2.0, 'Color', c_map{channel_no}(2,:));
    end
    
    xlim( ax, [time(1),time(end)]);
    
    % Add labels
    xlabel( ax, 'Time (s)');

    ylabel( ax, 'Current (pA)');
    
    set( ax, 'Fontsize', 20);
    
end