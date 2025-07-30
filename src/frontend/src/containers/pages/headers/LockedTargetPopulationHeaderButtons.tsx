import { LoadingButton } from '@components/core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { FileCopy } from '@mui/icons-material';
import { Box, Button, Tooltip } from '@mui/material';
import { BusinessArea } from '@restgenerated/models/BusinessArea';
import { Status791Enum } from '@restgenerated/models/Status791Enum';
import { TargetPopulationDetail } from '@restgenerated/models/TargetPopulationDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useProgramContext } from '../../../programContext';
import { DuplicateTargetPopulation } from '../../dialogs/targetPopulation/DuplicateTargetPopulation';
import { FinalizeTargetPopulationPaymentPlan } from '../../dialogs/targetPopulation/FinalizeTargetPopulationPaymentPlan';

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
  businessAreaData: BusinessArea;
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
  const { businessArea, programId } = useBaseUrl();
  const queryClient = useQueryClient();

  const { mutateAsync: unlockAction, isPending: loadingUnlock } = useMutation({
    mutationFn: () =>
      RestService.restBusinessAreasProgramsTargetPopulationsUnlockRetrieve({
        businessAreaSlug: businessArea,
        programSlug: programId,
        id: targetPopulation.id,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: [
          'targetPopulation',
          businessArea,
          targetPopulation.id,
          programId,
        ],
      });
      showMessage(t('Target Population Unlocked'));
    },
    onError: (error) => {
      showMessage(
        error.message ||
          t('An error occurred while unlocking the target population.'),
      );
    },
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
