function fig = plotRamp( rawData, stimTree, stimIndex, sampleRate, holdingValue)

    V_scale = 1e3;
    I_scale = 1e12;

    no_channels = size( rawData, 2);
    no_sweeps = 1;
    npts = size( rawData{1}, 1);
    dt = 1.0/sampleRate;

    time = (0:npts-1)*dt*1000;
    c_map = othercolor( 'Blues6', 2);

    % Scale data to mV and pA
    rawData{1} = rawData{1}*I_scale;
    rawData{2} = rawData{2}*V_scale;

    % Make stimulus figure
    fig = figure( 'Position', [0,0,1200,400]);

    % Make response figure
    ax1 = subplot( 1, 2, 1); hold on;
    ax2 = subplot( 1, 2, 2); hold on;
    stimLine = plot( ax1, time, rawData{2}, ...
      'Linewidth', 2.0, 'Color', c_map(2,:));
    dataLine = plot( ax2, time, rawData{1}, ...
      'Linewidth', 2.0, 'Color', c_map(2,:));

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
