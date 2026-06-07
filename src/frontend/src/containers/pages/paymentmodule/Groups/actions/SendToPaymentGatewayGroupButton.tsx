import { LoadingButton } from '@core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { Box } from '@mui/material';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { PaymentPlanGroupDetail } from '../types';
import { RestService } from '@restgenerated/index';

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

  const {
    mutateAsync: sendToPaymentGateway,
    isPending: loadingSend,
  } = useMutation({
    mutationFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlanGroupsSendToPaymentGatewayCreate({
        businessAreaSlug: businessArea,
        programCode: programId,
        id: group?.id,
      }),
    onSuccess: () => {
      showMessage(t('Sending to Payment Gateway started'));
      queryClient.invalidateQueries({
        queryKey: ['paymentPlanGroup', businessArea, programId, group.id],
      });
      queryClient.invalidateQueries({ queryKey: ['businessAreasPaymentPlans'] });
      queryClient.invalidateQueries({ queryKey: ['businessAreasProgramsPaymentPlansList'] });
    },
    onError: (error: any) => {
      showMessage(error?.message ?? t('Send to Payment Gateway failed'));
    },
  });

  if (!group) return null;


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
