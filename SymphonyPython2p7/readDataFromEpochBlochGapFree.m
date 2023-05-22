function data = readDataFromEpochBlochGapFree( epochBlock)
  % Reads data from epochBlock object into array
  epochs = epochBlock.getEpochs;
  no_epochs = length( epochs);
  
  data = [];
  for i = 1:no_epochs
    temp = epochs{i}.getResponses{1}.getData;
    data = [ data, temp];
  end
  
  plot(data);
  
end