import React, { useState } from 'react';
import styled from 'styled-components';
import { Box, Button } from '@material-ui/core';
import { EditRounded, Delete, FileCopy } from '@material-ui/icons';
import {TargetPopulationNode, TargetPopulationQuery} from '../../../__generated__/graphql';
import { DeleteTargetPopulation } from '../../dialogs/targetPopulation/DeleteTargetPopulation';
import { DuplicateTargetPopulation } from '../../dialogs/targetPopulation/DuplicateTargetPopulation';
import { LockTargetPopulationDialog } from '../../dialogs/targetPopulation/LockTargetPopulationDialog';

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

export interface InProgressTargetPopulationHeaderButtonsPropTypes {
  targetPopulation: TargetPopulationQuery['targetPopulation'];
  setEditState: Function;
  canDuplicate: boolean;
  canRemove: boolean;
  canEdit: boolean;
  canLock: boolean;
}

export const OpenTargetPopulationHeaderButtons = ({
  targetPopulation,
  setEditState,
  canDuplicate,
  canEdit,
  canLock,
  canRemove,
}: InProgressTargetPopulationHeaderButtonsPropTypes): React.ReactElement => {
  const [openApprove, setOpenApprove] = useState(false);
  const [openDuplicate, setOpenDuplicate] = useState(false);
  const [openDelete, setOpenDelete] = useState(false);
  return (
    <Box display='flex' alignItems='center'>
      {canDuplicate && (
        <IconContainer>
          <Button
            onClick={() => setOpenDuplicate(true)}
            data-cy='button-target-population-duplicate'
          >
            <FileCopy />
          </Button>
        </IconContainer>
      )}
      {canRemove && (
        <IconContainer>
          <Button onClick={() => setOpenDelete(true)}>
            <Delete />
          </Button>
        </IconContainer>
      )}
      {canEdit && (
        <Box m={2}>
          <Button
            variant='outlined'
            color='primary'
            startIcon={<EditRounded />}
            onClick={() => setEditState(true)}
          >
            Edit
          </Button>
        </Box>
      )}
      {canLock && (
        <Box m={2}>
          <Button
            variant='contained'
            color='primary'
            onClick={() => setOpenApprove(true)}
            data-cy='button-target-population-close'
          >
            Lock
          </Button>
        </Box>
      )}
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
      <LockTargetPopulationDialog
        open={openApprove}
        setOpen={setOpenApprove}
        targetPopulationId={targetPopulation.id}
      />
    </Box>
  );
};
