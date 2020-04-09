import React, { useState } from 'react';
import styled from 'styled-components';
import { Button } from '@material-ui/core';
import { EditRounded, Delete, FileCopy } from '@material-ui/icons';
import { TargetPopulationNode } from '../../../__generated__/graphql';
import { FinalizeTargetPopulation } from '../../dialogs/targetPopulation/FinalizeTargetPopulation';
import { DeleteTargetPopulation } from '../../dialogs/targetPopulation/DeleteTargetPopulation';
import { DuplicateTargetPopulation } from '../../dialogs/targetPopulation/DuplicateTargetPopulation';
import { ApproveCandidateList } from '../../dialogs/targetPopulation/ApproveCandidateList';

const IconContainer = styled.span`
  button {
    color: #949494;
    min-width: 40px;
    svg {
      width: 20px;
      height: 20px;
    }
  }
`;

const ButtonContainer = styled.span`
  margin: 0 ${({ theme }) => theme.spacing(2)}px;
`;

export interface InProgressTargetPopulationHeaderButtonsPropTypes {
  targetPopulation: TargetPopulationNode;
  setEditState: Function;
}

export function InProgressTargetPopulationHeaderButtons({
  targetPopulation,
  setEditState,
}: InProgressTargetPopulationHeaderButtonsPropTypes): React.ReactElement {
  const [openApprove, setOpenApprove] = useState(false);
  const [openDuplicate, setOpenDuplicate] = useState(false);
  const [openDelete, setOpenDelete] = useState(false);
  //TODO: Add finalize query and connect to dialog
  return (
    <div>
      <IconContainer>
        <Button onClick={() => setOpenDuplicate(true)}>
          <FileCopy />
        </Button>
      </IconContainer>
      <IconContainer>
        <Button onClick={() => setOpenDelete(true)}>
          <Delete />
        </Button>
      </IconContainer>
      <ButtonContainer>
        <Button
          variant='outlined'
          color='primary'
          startIcon={<EditRounded />}
          onClick={() => setEditState(true)}
        >
          Edit
        </Button>
      </ButtonContainer>
      <ButtonContainer>
        <Button
          variant='contained'
          color='primary'
          onClick={() => setOpenApprove(true)}
        >
          Approve
        </Button>
      </ButtonContainer>
      <DuplicateTargetPopulation
        open={openDuplicate}
        setOpen={setOpenDuplicate}
        targetPopulationId={targetPopulation.id}
      />
      <DeleteTargetPopulation
        open={openDelete}
        setOpen={setOpenDelete}
        targetPopulationId={targetPopulation.id}
      />
      <ApproveCandidateList
        open={openApprove}
        setOpen={setOpenApprove}
        targetPopulationId={targetPopulation.id}
      />
    </div>
  );
}
