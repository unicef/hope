import { Box, Button, Tooltip } from '@mui/material';
import { FileCopy } from '@mui/icons-material';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { LoadingButton } from '@components/core/LoadingButton';
import { useSnackbar } from '@hooks/useSnackBar';
import {
  Action,
  BusinessAreaDataQuery,
  PaymentPlanQuery,
  ProgramStatus,
} from '@generated/graphql';
import { DuplicateTargetPopulation } from '../../dialogs/targetPopulation/DuplicateTargetPopulation';
import { FinalizeTargetPopulationPaymentPlan } from '../../dialogs/targetPopulation/FinalizeTargetPopulationPaymentPlan';
import { useProgramContext } from '../../../programContext';
import { usePaymentPlanAction } from '@hooks/usePaymentPlanAction';
import { useNavigate } from 'react-router-dom';
import { useBaseUrl } from '@hooks/useBaseUrl';

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
  targetPopulation: PaymentPlanQuery['paymentPlan'];
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
  businessAreaData,
}: ApprovedTargetPopulationHeaderButtonsPropTypes): ReactElement {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { baseUrl } = useBaseUrl();
  const [openDuplicate, setOpenDuplicate] = useState(false);
  const [openFinalize, setOpenFinalize] = useState(false);
  const [openFinalizePaymentPlan, setOpenFinalizePaymentPlan] = useState(false);
  const { showMessage } = useSnackbar();
  const { isActiveProgram } = useProgramContext();

  //TODO: Action.TpUnlock
  const { mutatePaymentPlanAction: lockAction, loading: loadingLock } =
    usePaymentPlanAction(Action.TpLock, targetPopulationId, () => {
      showMessage(t('Target Population Finalized'));
      navigate(`/${baseUrl}/target-population/`);
      setOpenFinalize(false);
    });

  const { mutatePaymentPlanAction: unlockAction, loading: loadingUnlock } =
    usePaymentPlanAction(Action.TpLock, targetPopulationId, () => {
      showMessage(t('Target Population Finalized'));
      navigate(`/${baseUrl}/target-population/`);
      setOpenFinalize(false);
    });

  const { isPaymentPlanApplicable } = businessAreaData.businessArea;

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
            loading={loading}
            color="primary"
            variant="outlined"
            onClick={async () => {
              try {
                await mutate({
                  variables: { id: targetPopulation.id },
                });
                showMessage('Target Population Unlocked');
              } catch (e) {
                e.graphQLErrors.map((x) => showMessage(x.message));
              }
            }}
            data-cy="button-target-population-unlocked"
            disabled={!isActiveProgram}
          >
            Unlock
          </LoadingButton>
        </Box>
      )}
      {canSend && (
        <Box m={2}>
          {isPaymentPlanApplicable ? (
            <Tooltip
              title={
                targetPopulation.program.status !== ProgramStatus.Active
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
          ) : (
            <Tooltip
              title={
                targetPopulation.program.status !== ProgramStatus.Active
                  ? t('Assigned programme is not ACTIVE')
                  : t('Send to Cash Assist')
              }
            >
              <span>
                <Button
                  variant="contained"
                  color="primary"
                  disabled={
                    targetPopulation.program.status !== ProgramStatus.Active
                  }
                  onClick={() => setOpenFinalize(true)}
                  data-cy="button-target-population-send-to-cash-assist"
                >
                  {t('Send to Cash Assist')}
                </Button>
              </span>
            </Tooltip>
          )}
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
