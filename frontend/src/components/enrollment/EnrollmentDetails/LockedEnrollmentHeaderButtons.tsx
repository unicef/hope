import { Box, IconButton } from '@material-ui/core';
import { FileCopy } from '@material-ui/icons';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { LoadingButton } from '../../../components/core/LoadingButton';
import { useSnackbar } from '../../../hooks/useSnackBar';
import {
  TargetPopulationQuery,
  useUnlockTpMutation,
} from '../../../__generated__/graphql';
import { DuplicateEnrollment } from './DuplicateEnrollment';
import { FinalizeEnrollment } from './FinalizeEnrollment';

export interface LockedEnrollmentHeaderButtonsProps {
  targetPopulation: TargetPopulationQuery['targetPopulation'];
  canUnlock: boolean;
  canDuplicate: boolean;
}

export const LockedEnrollmentHeaderButtons = ({
  targetPopulation,
  canDuplicate,
  canUnlock,
}: LockedEnrollmentHeaderButtonsProps): React.ReactElement => {
  const { t } = useTranslation();
  const [openDuplicate, setOpenDuplicate] = useState(false);
  const [openFinalize, setOpenFinalize] = useState(false);
  const { showMessage } = useSnackbar();
  const [mutate, { loading }] = useUnlockTpMutation();

  return (
    <Box display='flex' alignItems='center'>
      {canDuplicate && (
        <IconButton onClick={() => setOpenDuplicate(true)}>
          <FileCopy />
        </IconButton>
      )}
      {canUnlock && (
        <Box m={2}>
          <LoadingButton
            loading={loading}
            color='primary'
            variant='outlined'
            onClick={() => {
              mutate({
                variables: { id: targetPopulation.id },
              }).then(() => {
                showMessage('Enrollment Unlocked');
              });
            }}
            data-cy='button-enrollment-unlocked'
          >
            Unlock
          </LoadingButton>
        </Box>
      )}
      <DuplicateEnrollment
        open={openDuplicate}
        setOpen={setOpenDuplicate}
        targetPopulationId={targetPopulation.id}
      />
      <FinalizeEnrollment
        open={openFinalize}
        setOpen={setOpenFinalize}
        targetPopulationId={targetPopulation.id}
        totalHouseholds={targetPopulation.totalHouseholdsCount}
      />
    </Box>
  );
};
