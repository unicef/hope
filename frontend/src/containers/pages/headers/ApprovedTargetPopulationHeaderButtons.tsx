import { Button, Tooltip } from '@material-ui/core';
import { FileCopy } from '@material-ui/icons';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useSnackbar } from '../../../hooks/useSnackBar';
import {
  TargetPopulationNode,
  useUnapproveTpMutation,
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

const ButtonContainer = styled.span`
  margin: 0 ${({ theme }) => theme.spacing(2)}px;
`;

export interface ApprovedTargetPopulationHeaderButtonsPropTypes {
  targetPopulation: TargetPopulationNode;
  canUnlock: boolean;
  canDuplicate: boolean;
  canSend: boolean;
}

export function ApprovedTargetPopulationHeaderButtons({
  targetPopulation,
  canSend,
  canDuplicate,
  canUnlock,
}: ApprovedTargetPopulationHeaderButtonsPropTypes): React.ReactElement {
  const { t } = useTranslation();
  const [openDuplicate, setOpenDuplicate] = useState(false);
  const [openFinalize, setOpenFinalize] = useState(false);
  const { showMessage } = useSnackbar();
  const [mutate] = useUnapproveTpMutation();

  return (
    <div>
      {canDuplicate && (
        <IconContainer>
          <Button onClick={() => setOpenDuplicate(true)}>
            <FileCopy />
          </Button>
        </IconContainer>
      )}
      {canUnlock && (
        <ButtonContainer>
          <Button
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
          </Button>
        </ButtonContainer>
      )}
      {canSend && (
        <ButtonContainer>
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
        </ButtonContainer>
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
        totalHouseholds={targetPopulation.finalListTotalHouseholds}
      />
    </div>
  );
}
