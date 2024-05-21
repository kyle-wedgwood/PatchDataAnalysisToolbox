% Function to collate results from all GJ step experiments
% Kyle Wedgwood
% 26.8.2019

function collatedData = collateData( collatedData, newData)

  if isempty( collatedData)
    collatedData = newData;
  else
    for i = 1:length( newData)
      ind = find( abs( newData(i).stim - vertcat( collatedData.stim, [])) < 0.01);
      if ~isempty(ind)
        collatedData(ind).response = [ collatedData(ind).response; newData(i).response];
      else
        collatedData(end+1).stim = newData(i).stim;
        collatedData(end).response = newData(i).response;
      end
    end
  end

end