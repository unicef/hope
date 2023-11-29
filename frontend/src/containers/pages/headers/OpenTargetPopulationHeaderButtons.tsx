import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Box, Button, IconButton } from '@material-ui/core';
import {
  EditRounded,
  Delete,
  FileCopy,
  RefreshRounded,
} from '@material-ui/icons';
import {
  ProgramStatus,
  TargetPopulationQuery,
  useRebuildTpMutation,
} from '../../../__generated__/graphql';
import { DeleteTargetPopulation } from '../../dialogs/targetPopulation/DeleteTargetPopulation';
import { DuplicateTargetPopulation } from '../../dialogs/targetPopulation/DuplicateTargetPopulation';
import { LockTargetPopulationDialog } from '../../dialogs/targetPopulation/LockTargetPopulationDialog';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { useProgramContext } from "../../../programContext";

export interface InProgressTargetPopulationHeaderButtonsPropTypes {
  targetPopulation: TargetPopulationQuery['targetPopulation'];
  canDuplicate: boolean;
  canRemove: boolean;
  canEdit: boolean;
  canLock: boolean;
}

export const OpenTargetPopulationHeaderButtons = ({
  targetPopulation,
  canDuplicate,
  canEdit,
  canLock,
  canRemove,
}: InProgressTargetPopulationHeaderButtonsPropTypes): React.ReactElement => {
  const [openLock, setOpenLock] = useState(false);
  const [openDuplicate, setOpenDuplicate] = useState(false);
  const [openDelete, setOpenDelete] = useState(false);
  const { baseUrl } = useBaseUrl();
  const { selectedProgram } = useProgramContext();

  const [
    rebuildTargetPopulation,
    { loading: rebuildTargetPopulationLoading },
  ] = useRebuildTpMutation();
  return (
    <Box display='flex' alignItems='center'>
      {canDuplicate && (
        <IconButton
          onClick={() => setOpenDuplicate(true)}
          data-cy='button-target-population-duplicate'
          disabled={selectedProgram?.status !== ProgramStatus.Active}
        >
          <FileCopy />
        </IconButton>
      )}
      {canRemove && (
        <IconButton
          data-cy='button-delete'
          onClick={() => setOpenDelete(true)}
          disabled={selectedProgram?.status !== ProgramStatus.Active}
        >
          <Delete />
        </IconButton>
      )}
      {canEdit && (
        <Box m={2}>
          <Button
            data-cy='button-edit'
            variant='outlined'
            color='primary'
            startIcon={<EditRounded />}
            component={Link}
            to={`/${baseUrl}/target-population/edit-tp/${targetPopulation.id}`}
            disabled={selectedProgram?.status !== ProgramStatus.Active}
          >
            Edit
          </Button>
        </Box>
      )}
      {canEdit && (
        <Box m={2}>
          <Button
            data-cy='button-rebuild'
            variant='outlined'
            color='primary'
            disabled={rebuildTargetPopulationLoading || selectedProgram?.status !== ProgramStatus.Active}
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
            disabled={selectedProgram?.status !== ProgramStatus.Active}
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
