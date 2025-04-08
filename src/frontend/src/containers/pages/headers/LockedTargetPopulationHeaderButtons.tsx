import { LoadingButton } from '@components/core/LoadingButton';
import { Action, BusinessAreaDataQuery } from '@generated/graphql';
import { usePaymentPlanAction } from '@hooks/usePaymentPlanAction';
import { useSnackbar } from '@hooks/useSnackBar';
import { FileCopy } from '@mui/icons-material';
import { Box, Button, Tooltip } from '@mui/material';
import { TargetPopulationDetail } from '@restgenerated/models/TargetPopulationDetail';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useProgramContext } from '../../../programContext';
import { DuplicateTargetPopulation } from '../../dialogs/targetPopulation/DuplicateTargetPopulation';
import { FinalizeTargetPopulationPaymentPlan } from '../../dialogs/targetPopulation/FinalizeTargetPopulationPaymentPlan';
import { Status791Enum } from '@restgenerated/models/Status791Enum';

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
  targetPopulation: TargetPopulationDetail;
  canUnlock: boolean;
  canDuplicate: boolean;
  canSend: boolean;
  businessAreaData: BusinessAreaDataQuery;
}

export function LockedTargetPopulationHeaderButtons({
  targetPopulation,
  canSend,
  canDuplicate,
  canUnlock,
}: ApprovedTargetPopulationHeaderButtonsPropTypes): ReactElement {
  const { t } = useTranslation();
  const [openDuplicate, setOpenDuplicate] = useState(false);
  const [openFinalizePaymentPlan, setOpenFinalizePaymentPlan] = useState(false);
  const { showMessage } = useSnackbar();
  const { isActiveProgram } = useProgramContext();

  const { mutatePaymentPlanAction: unlockAction, loading: loadingUnlock } =
    usePaymentPlanAction(Action.TpUnlock, targetPopulation.id, () => {
      showMessage(t('Target Population Unlocked'));
    });

  return (
    <Box display="flex" alignItems="center">
      {canDuplicate && (
        <IconContainer>
          <Button
            onClick={() => setOpenDuplicate(true)}
            disabled={!isActiveProgram}
          >
            <FileCopy />
          </Button>
        </IconContainer>
      )}
      {canUnlock && (
        <Box m={2}>
          <LoadingButton
            loading={loadingUnlock}
            color="primary"
            variant="outlined"
            onClick={() => unlockAction()}
            data-cy="button-target-population-unlocked"
            disabled={!isActiveProgram}
          >
            Unlock
          </LoadingButton>
        </Box>
      )}
      {canSend && (
        <Box m={2}>
          <Tooltip
            title={
              targetPopulation.program.status !== Status791Enum.ACTIVE
                ? t('Assigned programme is not ACTIVE')
                : ''
            }
          >
            <span>
              <Button
                variant="contained"
                color="primary"
                disabled={!isActiveProgram}
                onClick={() => setOpenFinalizePaymentPlan(true)}
                data-cy="button-target-population-send-to-hope"
              >
                {t('Mark Ready')}
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
      <FinalizeTargetPopulationPaymentPlan
        open={openFinalizePaymentPlan}
        setOpen={setOpenFinalizePaymentPlan}
        targetPopulationId={targetPopulation.id}
        totalHouseholds={targetPopulation.totalHouseholdsCount}
      />
    </Box>
  );
}
