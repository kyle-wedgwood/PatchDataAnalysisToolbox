function data = readDataFromEpochBlockPulseFamily( epochBlock)
  % Reads data from epochBlock object into array
  epochs = epochBlock.getEpochs;
  epoch_par_vals = epochBlock.protocolParameters.values;
  no_epochs = length( epochs);
  no_ave = epoch_par_vals{5};
  no_pulses = no_epochs/no_ave;
  for j = 1:no_ave
    for i = 1:no_pulses
      temp = epochs{i+(j-1)*no_pulses}.getResponses{1}.getData;
      if (i*j == 1)
        no_pts = length( temp);
        data = zeros( no_pulses, no_pts);
      end
      data(i,:) = data(i,:) + temp;
    end
  end
  
  data = data.'/double( no_ave);
  
  plot(data);
  
end