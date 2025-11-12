import { Box, Button } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useProgramContext } from '../../../../../programContext';
import { ReactElement, useState } from 'react';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { PERMISSIONS } from 'src/config/permissions';

export interface AbortedPaymentPlanHeaderButtonsProps {
  paymentPlan: PaymentPlanDetail;
  canReactivate: boolean;
}

export function AbortedPaymentPlanHeaderButtons({
  paymentPlan,
  canReactivate,
}: AbortedPaymentPlanHeaderButtonsProps): ReactElement {
  const { t } = useTranslation();
  const { isActiveProgram } = useProgramContext();
  const { businessArea, programId } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();
  const [loading, setLoading] = useState(false);

  const { mutateAsync: reactivate } = useMutation({
    mutationFn: async () => {
      setLoading(true);
      await RestService.restBusinessAreasProgramsPaymentPlansReactivateAbortRetrieve(
        {
          businessAreaSlug: businessArea,
          id: paymentPlan.id,
          programSlug: programId,
        },
      );
      setLoading(false);
    },
    onSuccess: () => {
      showMessage(t('Payment Plan has been reactivated.'));
      queryClient.invalidateQueries({
        queryKey: ['paymentPlan', businessArea, paymentPlan.id, programId],
      });
    },
    onError: () => {
      setLoading(false);
    },
  });

  const handleReactivate = async () => {
    await reactivate();
  };

  return (
    <Box display="flex" alignItems="center">
      {canReactivate && (
        <Box m={2}>
          <Button
            variant="contained"
            color="primary"
            data-cy="button-reactivate-payment-plan"
            onClick={handleReactivate}
            disabled={!isActiveProgram || loading}
            data-perm={PERMISSIONS.PM_REACTIVATE_ABORT}
          >
            {loading ? t('Reactivating...') : t('Reactivate')}
          </Button>
        </Box>
      )}
    </Box>
  );
}
