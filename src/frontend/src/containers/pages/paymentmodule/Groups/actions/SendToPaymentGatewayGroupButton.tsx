import { LoadingButton } from '@core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { Box } from '@mui/material';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { PaymentPlanGroupDetail } from '../types';

interface SendToPaymentGatewayGroupButtonProps {
  group: PaymentPlanGroupDetail | null;
}

export function SendToPaymentGatewayGroupButton({
  group,
}: SendToPaymentGatewayGroupButtonProps): ReactElement | null {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();

  if (!group) return null;

  const {
    mutateAsync: sendToPaymentGateway,
    isPending: loadingSend,
  } = useMutation({
    mutationFn: async () => {
      // TODO (TICKET-9): implement once backend adds the send-to-payment-gateway action
      // RestService.restBusinessAreasProgramsPaymentPlanGroupsSendToPaymentGatewayCreate({
      //   businessAreaSlug: businessArea, programCode: programId, id: group.id,
      // })
      // TODO (TICKET-9): button visibility should be conditioned on group status once that field exists
      throw new Error('Send to Payment Gateway endpoint not yet available');
    },
    onSuccess: () => {
      showMessage(t('Sending to Payment Gateway started'));
      queryClient.invalidateQueries({
        queryKey: ['paymentPlanGroup', businessArea, programId, group.id],
      });
    },
    onError: (error: any) => {
      showMessage(error?.message ?? t('Send to Payment Gateway failed'));
    },
  });

  const isDisabled = loadingSend;

  return (
    <Box m={2}>
      <LoadingButton
        loading={loadingSend}
        color="primary"
        variant="contained"
        onClick={() => sendToPaymentGateway()}
        disabled={isDisabled}
        data-cy="button-send-to-payment-gateway-group"
      >
        {t('Send to Payment Gateway')}
      </LoadingButton>
    </Box>
  );
}
