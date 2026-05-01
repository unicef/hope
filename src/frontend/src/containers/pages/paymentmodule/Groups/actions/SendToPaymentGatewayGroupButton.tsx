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
  const { businessArea } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();

  // TODO: Determine which group statuses allow Send to Payment Gateway
  // For now, the button is always rendered when a group exists
  if (!group) return null;

  const {
    mutateAsync: sendToPaymentGateway,
    isPending: loadingSend,
  } = useMutation({
    mutationFn: async () => {
      // TODO: RestService.restBusinessAreasPaymentPlanGroupsSendToPaymentGatewayCreate({ businessAreaSlug: businessArea, id: group.id })
      // Endpoint: POST /api/rest/business-areas/{ba_slug}/payment-plan-groups/{id}/send-to-payment-gateway/
      throw new Error('Send to Payment Gateway endpoint not yet available');
    },
    onSuccess: () => {
      showMessage(t('Sending to Payment Gateway started'));
      queryClient.invalidateQueries({
        queryKey: ['paymentPlanGroup', businessArea, group.id],
      });
    },
    onError: (error: any) => {
      showMessage(error?.message ?? t('Send to Payment Gateway failed'));
    },
  });

  const isDisabled = loadingSend || Boolean(group.backgroundActionStatus);

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
