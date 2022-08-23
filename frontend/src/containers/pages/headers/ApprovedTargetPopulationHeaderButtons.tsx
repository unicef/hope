import { Box, Button, Tooltip } from '@material-ui/core';
import { FileCopy } from '@material-ui/icons';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { LoadingButton } from '../../../components/core/LoadingButton';
import { useSnackbar } from '../../../hooks/useSnackBar';
import {
  TargetPopulationNode,
  useUnlockTpMutation,
} from '../../../__generated__/graphql';
import { DuplicateTargetPopulation } from '../../dialogs/targetPopulation/DuplicateTargetPopulation';
import { FinalizeTargetPopulation } from '../../dialogs/targetPopulation/FinalizeTargetPopulation';

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

export interface ApprovedTargetPopulationHeaderButtonsPropTypes {
  targetPopulation: TargetPopulationNode;
  canUnlock: boolean;
  canDuplicate: boolean;
  canSend: boolean;
}

export const ApprovedTargetPopulationHeaderButtons = ({
  targetPopulation,
  canSend,
  canDuplicate,
  canUnlock,
}: ApprovedTargetPopulationHeaderButtonsPropTypes): React.ReactElement => {
  const { t } = useTranslation();
  const [openDuplicate, setOpenDuplicate] = useState(false);
  const [openFinalize, setOpenFinalize] = useState(false);
  const { showMessage } = useSnackbar();
  const [mutate, { loading }] = useUnlockTpMutation();

  return (
    <Box display='flex' alignItems='center'>
      {canDuplicate && (
        <IconContainer>
          <Button onClick={() => setOpenDuplicate(true)}>
            <FileCopy />
          </Button>
        </IconContainer>
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
                showMessage('Target Population Unlocked');
              });
            }}
            data-cy='button-target-population-unlocked'
          >
            Unlock
          </LoadingButton>
        </Box>
      )}
      {canSend && (
        <Box m={2}>
          <Tooltip
            title={
              targetPopulation.program.status !== 'ACTIVE'
                ? t('Assigned programme is not ACTIVE')
                : t('Send to Cash Assist')
            }
          >
            <span>
              <Button
                variant='contained'
                color='primary'
                disabled={targetPopulation.program.status !== 'ACTIVE'}
                onClick={() => setOpenFinalize(true)}
                data-cy='button-target-population-send-to-cash-assist'
              >
                {t('Send to Cash Assist')}
              </Button>
            </span>
          </Tooltip>
        </Box>
      )}
      <DuplicateTargetPopulation
        open={openDuplicate}
        setOpen={setOpenDuplicate}
        targetPopulationId={targetPopulation.id}
      />
      <FinalizeTargetPopulation
        open={openFinalize}
        setOpen={setOpenFinalize}
        targetPopulationId={targetPopulation.id}
        totalHouseholds={targetPopulation.totalHouseholdsCount}
      />
    </Box>
  );
};
