import React, { useState } from 'react';
import styled from 'styled-components';
import { Box, Button } from '@material-ui/core';
import {
  EditRounded,
  Delete,
  FileCopy,
  RefreshRounded,
} from '@material-ui/icons';
import {
  TargetPopulationQuery,
  useRebuildTpMutation,
} from '../../../__generated__/graphql';
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
  const [openLock, setOpenLock] = useState(false);
  const [openDuplicate, setOpenDuplicate] = useState(false);
  const [openDelete, setOpenDelete] = useState(false);

  const [
    rebuildTargetPopulation,
    { loading: rebuildTargetPopulationLoading },
  ] = useRebuildTpMutation();
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
      {canEdit && (
        <Box m={2}>
          <Button
            variant='outlined'
            color='primary'
            disabled={rebuildTargetPopulationLoading}
            startIcon={<RefreshRounded />}
            onClick={() =>
              rebuildTargetPopulation({
                variables: { id: targetPopulation.id },
              })
            }
          >
            Rebuild
          </Button>
        </Box>
      )}
      {canLock && (
        <Box m={2}>
          <Button
            variant='contained'
            color='primary'
            onClick={() => setOpenLock(true)}
            data-cy='button-target-population-lock'
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
        open={openLock}
        setOpen={setOpenLock}
        targetPopulationId={targetPopulation.id}
      />
    </Box>
  );
};
