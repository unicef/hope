import { Box, Button } from '@mui/material';
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
import { PERMISSIONS } from 'src/config/permissions';

export interface AcceptedPaymentPlanHeaderButtonsProps {
  canSendToPaymentGateway: boolean;
  canSplit: boolean;
  paymentPlan: PaymentPlanDetail;
  canClose: boolean;
  isInstructionManaged?: boolean;
}

export function AcceptedPaymentPlanHeaderButtons({
  canSendToPaymentGateway,
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

  const { mutateAsync: sendXlsxPassword, isPending: loadingSend } = useMutation({
    mutationFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlansSendXlsxPasswordRetrieve({
        businessAreaSlug: businessArea,
        programCode: programId,
        id: paymentPlan.id,
      }),
    onSuccess: () => {
      showMessage(t('Password has been sent.'));
    },
    onError: (error: any) => {
      showApiErrorMessages(error, showMessage);
    },
  });

  const {
    mutateAsync: sendToPaymentGateway,
    isPending: LoadingSendToPaymentGateway,
  } = useMutation({
    mutationFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlansSendToPaymentGatewayRetrieve(
        {
          businessAreaSlug: businessArea,
          programCode: programId,
          id: paymentPlan.id,
        },
      ),
    onSuccess: () => {
      showMessage(t('Sending to Payment Gateway started'));
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
        {/* FSP delivery export + download moved to the Group / Batch detail pages. */}
        {paymentPlan.hasPaymentListExportFile &&
          paymentPlan.canSendXlsxPassword &&
          !isInstructionManaged && (
            <Box m={2}>
              <LoadingButton
                loading={loadingSend}
                disabled={loadingSend}
                color="primary"
                variant="contained"
                data-cy="button-send-xlsx-password"
                onClick={() => sendXlsxPassword()}
                data-perm={PERMISSIONS.PM_SEND_XLSX_PASSWORD}
              >
                {t('Send Xlsx Password')}
              </LoadingButton>
            </Box>
          )}

        {canSendToPaymentGateway && !isInstructionManaged && (
          <Box m={2}>
            <Button
              type="button"
              color="primary"
              variant="contained"
              onClick={() => sendToPaymentGateway()}
              data-cy="button-send-to-payment-gateway"
              disabled={LoadingSendToPaymentGateway}
              data-perm={PERMISSIONS.PM_SEND_TO_PAYMENT_GATEWAY}
            >
              {t('Send to FSP')}
            </Button>
          </Box>
        )}
      </>
    </Box>
  );
}
