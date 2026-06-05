import { Box } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useSnackbar } from '@hooks/useSnackBar';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { LoadingButton } from '../../../../core/LoadingButton';
import { CreateChildPaymentPlan } from '../../../CreateChildPaymentPlan';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation } from '@tanstack/react-query';
import { SplitIntoPaymentLists } from '../SplitIntoPaymentLists';
import { ReactElement } from 'react';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { showApiErrorMessages } from '@utils/utils';

export interface AcceptedPaymentPlanHeaderButtonsProps {
  canSplit: boolean;
  paymentPlan: PaymentPlanDetail;
  canClose: boolean;
  isInstructionManaged?: boolean;
}

export function AcceptedPaymentPlanHeaderButtons({
  canSplit,
  paymentPlan,
  canClose,
  isInstructionManaged = false,
}: AcceptedPaymentPlanHeaderButtonsProps): ReactElement {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const { businessArea, programId } = useBaseUrl();

  const { mutateAsync: closePaymentPlan, isPending: loadingClose } =
    useMutation({
      mutationFn: async () => {
        return RestService.restBusinessAreasProgramsPaymentPlansCloseRetrieve({
          businessAreaSlug: businessArea,
          programCode: programId,
          id: paymentPlan.id,
        });
      },
      onSuccess: () => {
        showMessage(t('Payment plan closed successfully'));
      },
      onError: (error: any) => {
        showApiErrorMessages(error, showMessage);
      },
    });

  return (
    <Box display="flex" alignItems="center">
      <>
        {paymentPlan.canCreateFollowUp && (
          <Box p={2}>
            <CreateChildPaymentPlan paymentPlan={paymentPlan} variant="followup" />
          </Box>
        )}
        {paymentPlan.canCreateTopUp && (
          <Box p={2}>
            <CreateChildPaymentPlan paymentPlan={paymentPlan} variant="topup" />
          </Box>
        )}
        {paymentPlan.canCreateTopUpAmendment && (
          <Box p={2}>
            <CreateChildPaymentPlan
              paymentPlan={paymentPlan}
              variant="amendment"
            />
          </Box>
        )}
        {!isInstructionManaged && (
          <Box p={2}>
            <SplitIntoPaymentLists
              paymentPlan={paymentPlan}
              canSplit={canSplit}
            />
          </Box>
        )}
        {canClose && !isInstructionManaged && (
          <Box m={2}>
            <LoadingButton
              color="primary"
              variant="contained"
              data-cy="button-close"
              onClick={() => closePaymentPlan()}
              loading={loadingClose}
            >
              {t('Close')}
            </LoadingButton>
          </Box>
        )}
        {/* Send Xlsx Password and Send to FSP moved to the Group / Batch detail pages. */}
      </>
    </Box>
  );
}
