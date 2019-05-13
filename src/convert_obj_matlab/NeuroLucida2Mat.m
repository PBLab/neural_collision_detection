function neuron = NeuroLucida2Mat (filename)
% Parses .ASC files into a .mat object which can be serialized later.
% we will process each line separatedly and define what line "types":
%
% Feature definition -
%     "Cell Body", "Dendrite" or "Axon"
%
% Feature termination -
%       End of contour - finishes Cell Body
%       ( - finishes a segment
%        Normal/Incomplete terminate branches
%       |
%       )  ;  End of split - ends of an entire branch

clc
neuron = struct('CellBody',[],'Dendrites',[],'Axon',[]);
iCountoursInCellBody = 0;
numOfAxons=0;
numOfDendrites=0;


fid = fopen(filename,'r');
disp(filename)
while 1
    currentLine = fgetl(fid); 
    if ~ischar(currentLine), break,
        
    elseif ~isempty(strfind(currentLine,'Cell')) && ~isempty(strfind(currentLine,'Body'))
        disp('Working on cell body')
        iCountoursInCellBody = iCountoursInCellBody+1;
        thisCountourCoord =[];
        %call function to get cell body
        %get two lines - these do not contain numeric data
        currentWorkingLine = fgetl(fid); % first line doesn't contain data
        currentWorkingLine = fgetl(fid); % second line doesn't contain data
        %cycle to
        width =[];
        moreCellData = 1;
        ind = 1;
        while moreCellData
            currentWorkingLine = fgetl(fid);
            currentData=textscan(currentWorkingLine,'(%n%n%n%n) ;%n,%n'); % cell body data formatted as (x y z w) cID pID
            if strfind(currentWorkingLine,'End of contour');break;
            elseif ~isempty(currentData{1})
                % end of countour - end of cell body
                thisCountourCoord(ind,:) = cell2mat(currentData(:,1:3));%get the first three numbers
                width(ind,:)=cell2mat(currentData(:,4));
                ID(ind,:)=cell2mat(currentData(:,5:6));
                ind = ind+1;
            end
            
        end
        neuron.CellBody.ContourLine(iCountoursInCellBody).coords = thisCountourCoord;
        neuron.CellBody.ContourLine(iCountoursInCellBody).width = width;  
        neuron.CellBody.ContourLine(iCountoursInCellBody).ID = ID;
        
    elseif ~isempty(strfind(currentLine,'Axon'))
        
        disp('Working on axon');
        numOfAxons=numOfAxons+1; % moves to next axon (can be removed as there's only one axon)
        contInd=1;
        currentWorkingLine = fgetl(fid); % next line
        currentData=textscan(currentWorkingLine,'(%n%n%n%n)');
        % root exit point:
        neuron.Axon(numOfAxons).ContourLine(1).coords=cell2mat(currentData(:,1:3));
        neuron.Axon(numOfAxons).ContourLine(1).width(:) = cell2mat(currentData(:,4));
        neuron.Axon(numOfAxons).ContourLine(1).ID = [0 0];
        
        
        
        currentBranch=0;
        line=0;
        while 1
            
            currentWorkingLine = fgetl(fid);
            currentData=textscan(currentWorkingLine,'(%n%n%n)'); %repmat('%n',1,3)
            if ~isempty(strfind(currentWorkingLine,'End of tree'))
                break
            elseif ~isempty(currentData{1})
                if ~isempty(strfind(currentWorkingLine,'R')) % start of new root
                    contInd=contInd+1;
                    line=0;
                    currentBranch=currentBranch+1;
                    % getting branch ID:
                    tempSplit=currentWorkingLine(strfind(currentWorkingLine,'R'):end);
                    tempSplit(tempSplit=='R' | tempSplit=='-')=[];
                    if isempty(tempSplit)
                        trunkID=0;
                    else
                        trunkID=str2double(tempSplit);
                    end
                    % creating branch point list for adjacency matrix:
                    neuron.Axon(numOfAxons).branchPointList(contInd-1)=trunkID;
                end
                
                line=line+1;
                currentData=textscan(currentWorkingLine,'(%n%n%n%n) ;%n'); % extracts data
                neuron.Axon(numOfAxons).ContourLine(contInd).coords(line,:) = cell2mat(currentData(:,1:3));
                neuron.Axon(numOfAxons).ContourLine(contInd).width(line,:) = cell2mat(currentData(:,4));
                neuron.Axon(numOfAxons).ContourLine(contInd).ID(line,:) = [trunkID cell2mat(currentData(:,5))];
                
                % adjacency matrix:
                if cell2mat(currentData(:,5))==1 && trunkID~=0
                    if length(num2str(trunkID))==1
                        neuron.Axon(numOfAxons).adjMat(contInd-1,1) = -1;
                        neuron.Axon(numOfAxons).adjMat(1,contInd-1) = 1;
                    else
                        tempBranch=num2str(trunkID);
                        parentBranch=find(neuron.Axon(numOfAxons).branchPointList==str2double(tempBranch(1:(end-1))));
                        neuron.Axon(numOfAxons).adjMat(contInd-1,parentBranch) = -1;
                        neuron.Axon(numOfAxons).adjMat(parentBranch,contInd-1) = 1;
                    end
                end
            end
        end
        
        
    elseif ~isempty(strfind(currentLine,'Dendrite'))
        disp('Working on dendrite');
        numOfDendrites=numOfDendrites+1;
        contInd=1;
        currentWorkingLine = fgetl(fid);
        currentData=textscan(currentWorkingLine,'(%n%n%n%n)');
        neuron.Dendrites(numOfDendrites).ContourLine(1).coords=cell2mat(currentData(:,1:3));
        neuron.Dendrites(numOfDendrites).ContourLine(1).width(:) = cell2mat(currentData(:,4));
        neuron.Dendrites(numOfDendrites).ContourLine(1).ID = [0 0];
        
        currentBranch=0;
        line=0;
        while 1
            
            currentWorkingLine = fgetl(fid);
            currentData=textscan(currentWorkingLine,'(%n%n%n)'); 
            if ~isempty(strfind(currentWorkingLine,'End of tree'))
                break
            elseif ~isempty(currentData{1})
                if ~isempty(strfind(currentWorkingLine,'R'))
                    contInd=contInd+1;
                    line=0;
                    currentBranch=currentBranch+1;
                    tempSplit=currentWorkingLine(strfind(currentWorkingLine,'R'):end);
                    tempSplit(tempSplit=='R' | tempSplit=='-')=[];
                    if isempty(tempSplit)
                        trunkID=0;
                    else
                        trunkID=str2double(tempSplit);
                    end
                    neuron.Dendrites(numOfDendrites).branchPointList(contInd-1)=trunkID;
                end
                
                line=line+1;
                currentData=textscan(currentWorkingLine,'(%n%n%n%n) ;%n');
                neuron.Dendrites(numOfDendrites).ContourLine(contInd).coords(line,:) = cell2mat(currentData(:,1:3));
                neuron.Dendrites(numOfDendrites).ContourLine(contInd).width(line,:) = cell2mat(currentData(:,4));
                neuron.Dendrites(numOfDendrites).ContourLine(contInd).ID(line,:) = [trunkID cell2mat(currentData(:,5))];
                  
                if cell2mat(currentData(:,5))==1 && trunkID~=0
                    if length(num2str(trunkID))==1
                        neuron.Dendrites(numOfDendrites).adjMat(contInd-1,1) = -1;
                        neuron.Dendrites(numOfDendrites).adjMat(1,contInd-1) = 1;
                    else
                        tempBranch=num2str(trunkID);
                        parentBranch=find(neuron.Dendrites(numOfDendrites).branchPointList==str2double(tempBranch(1:(end-1))));
                        neuron.Dendrites(numOfDendrites).adjMat(contInd-1,parentBranch) = -1;
                        neuron.Dendrites(numOfDendrites).adjMat(parentBranch,contInd-1) = 1;
                    end
                end
            end
        end
    end
    
    
end


fclose(fid);
save(filename(1:(end-4)),'neuron');
end

