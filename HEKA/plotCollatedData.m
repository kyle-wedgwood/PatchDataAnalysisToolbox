% Function to plot collated responses
% Kyle Wedgwood
% 26.8.2019

function [fig,ax] = plotCollatedData( collatedDataSets, x_label, y_label, labels, fig, ax)

  if nargin < 5
    fig = figure( 'Position', [0,0,1200,800]);
    ax = axes( fig); hold on;
  end
  
  h = gobjects( length( collatedDataSets), 1);
  
  for i = 1:length( collatedDataSets)
    
    collatedData = collatedDataSets{i};
    x_data = vertcat( collatedData.stim, []);
    y_data = zeros( size( x_data));
    std_data = zeros( size( y_data));
    sem_data = zeros( size( y_data));

    for response_no = 1:length( collatedData)
      y_data(response_no,:)   = mean( collatedData(response_no).response(:), 1);
      std_data(response_no,:) = std( collatedData(response_no).response(:));
      sem_data(response_no,:)  = std_data( response_no)/sqrt( size( collatedData(response_no).response, 1));
    end

    h(i) = plot( ax, x_data, y_data, 'Linewidth', 4.0);
    color = get( h(i), 'Color');
    errorbar( ax, x_data, y_data, sem_data, 'Color', color,  'Linewidth', 2.0);
    
    N = length( collatedData( 1).response(:));
    labels{i} = sprintf( '%s : N = %d', labels{i}, N);

  end
  
  x_lim = get( gca, 'XLim');
  line( [x_lim(1),x_lim(2)], [0,0], 'Linewidth', 4.0, 'Linestyle', ':', 'Color', 0.5*ones(1,3)); 

  xlabel( x_label);
  ylabel( y_label);
  legend( h, labels);
  
  set( gca, 'Fontsize', 24);
  
end