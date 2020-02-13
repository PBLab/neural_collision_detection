function VectorizeNeuron(filename)
load(filename);
neuron.vectorizedStructure.AllVerts = [];
neuron.vectorizedStructure.AllRadii = [];
neuron.vectorizedStructure.JunctionsANDEnds = [];
temp_verts = vertcat(neuron.Axon.ContourLine.coords);
temp_radii = vertcat(neuron.Axon.ContourLine.width);
neuron.vectorizedStructure.AllVerts((end+1):(end+size(temp_verts,1)),:) = temp_verts;
neuron.vectorizedStructure.AllRadii((end+1):(end+size(temp_radii,1)),:) = temp_radii;
neuron.vectorizedStructure.JunctionsANDEnds(end+1) = 0;
for ind=2:length(neuron.Axon.ContourLine)
    
    neuron.vectorizedStructure.JunctionsANDEnds(end+size(neuron.Axon.ContourLine(ind).coords,1)) = 1;
end

for i=1:length(neuron.Dendrites)
    temp_verts = vertcat(neuron.Dendrites(i).ContourLine.coords);
    temp_radii = vertcat(neuron.Dendrites(i).ContourLine.width);
    neuron.vectorizedStructure.AllVerts((end+1):(end+size(temp_verts,1)),:) = temp_verts;
    neuron.vectorizedStructure.AllRadii((end+1):(end+size(temp_radii,1)),:) = temp_radii;
    neuron.vectorizedStructure.JunctionsANDEnds(end+1) = 0;
    for ind=2:length(neuron.Dendrites(i).ContourLine)
        
        neuron.vectorizedStructure.JunctionsANDEnds(end+size(neuron.Dendrites(i).ContourLine(ind).coords,1)) = 1;
    end
end

for i = 1:length(neuron.CellBody)
   temp_verts = vertcat(neuron.CellBody(i).ContourLine.coords);
   temp_radii = vertcat(neuron.CellBody(i).ContourLine.width);
   neuron.vectorizedStructure.AllVerts((end + 1):(end + size(temp_verts, 1)), :) = temp_verts;
   neuron.vectorizedStructure.AllRadii((end + 1):(end + size(temp_radii, 1)), :) = temp_radii;
   neuron.vectorizedStructure.JunctionsANDEnds(end + 1) = 0;
   for ind = 2:length(neuron.CellBody(i).ContourLine)
       neuron.vectorizedStructure.JunctionsANDEnds(end + size(neuron.CellBody(i).ContourLine(ind).coords, 1)) = 1;
   end
end
neuron.vectorizedStructure.JunctionsANDEnds = logical(neuron.vectorizedStructure.JunctionsANDEnds');
save(filename,'neuron');
end