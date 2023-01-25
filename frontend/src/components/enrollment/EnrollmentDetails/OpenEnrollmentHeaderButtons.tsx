import { Box, Button, IconButton } from '@material-ui/core';
import {
  Delete,
  EditRounded,
  FileCopy,
  RefreshRounded,
} from '@material-ui/icons';
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import {
  TargetPopulationQuery,
  useRebuildTpMutation,
} from '../../../__generated__/graphql';
import { DeleteEnrollment } from './DeleteEnrollment';
import { DuplicateEnrollment } from './DuplicateEnrollment';
import { LockEnrollment } from './LockEnrollment';

export interface OpenEnrollmentHeaderButtonsProps {
  targetPopulation: TargetPopulationQuery['targetPopulation'];
  canDuplicate: boolean;
  canRemove: boolean;
  canEdit: boolean;
  canLock: boolean;
}

export const OpenEnrollmentHeaderButtons = ({
  targetPopulation,
  canDuplicate,
  canEdit,
  canLock,
  canRemove,
}: OpenEnrollmentHeaderButtonsProps): React.ReactElement => {
  const [openApprove, setOpenApprove] = useState(false);
  const [openDuplicate, setOpenDuplicate] = useState(false);
  const [openDelete, setOpenDelete] = useState(false);
  const businessArea = useBusinessArea();

  const [
    rebuildTargetPopulation,
    { loading: rebuildTargetPopulationLoading },
  ] = useRebuildTpMutation();
  return (
    <Box display='flex' alignItems='center'>
      {canDuplicate && (
        <IconButton
          onClick={() => setOpenDuplicate(true)}
          data-cy='button-enrollment-duplicate'
        >
          <FileCopy />
        </IconButton>
      )}
      {canRemove && (
        <IconButton onClick={() => setOpenDelete(true)}>
          <Delete />
        </IconButton>
      )}
      {canEdit && (
        <Box m={2}>
          <Button
            variant='outlined'
            color='primary'
            startIcon={<EditRounded />}
            component={Link}
            to={`/${businessArea}/enrollment/edit-enrollment/${targetPopulation.id}`}
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
            onClick={() => setOpenApprove(true)}
            data-cy='button-enrollment-lock'
          >
            Lock
          </Button>
        </Box>
      )}
      <DuplicateEnrollment
        open={openDuplicate}
        setOpen={setOpenDuplicate}
        targetPopulationId={targetPopulation.id}
      />
      <DeleteEnrollment
        open={openDelete}
        setOpen={setOpenDelete}
        targetPopulationId={targetPopulation.id}
      />
      <LockEnrollment
        open={openApprove}
        setOpen={setOpenApprove}
        targetPopulationId={targetPopulation.id}
      />
    </Box>
  );
};
