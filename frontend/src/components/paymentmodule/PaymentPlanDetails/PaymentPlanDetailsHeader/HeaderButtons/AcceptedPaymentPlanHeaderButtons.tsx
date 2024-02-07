import { Box, Button } from '@mui/material';
import { GetApp } from '@mui/icons-material';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { useSnackbar } from '../../../../../hooks/useSnackBar';
import {
  Action,
  PaymentPlanBackgroundActionStatus,
  PaymentPlanQuery,
  useExportXlsxPpListPerFspMutation,
} from '../../../../../__generated__/graphql';
import { LoadingButton } from '../../../../core/LoadingButton';
import { CreateFollowUpPaymentPlan } from '../../../CreateFollowUpPaymentPlan';
import { useProgramContext } from '../../../../../programContext';
import { usePaymentPlanAction } from '../../../../../hooks/usePaymentPlanAction';

export interface AcceptedPaymentPlanHeaderButtonsProps {
  canDownloadXlsx: boolean;
  canExportXlsx: boolean;
  canSendToPaymentGateway: boolean;
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export function AcceptedPaymentPlanHeaderButtons({
  canDownloadXlsx,
  canExportXlsx,
  canSendToPaymentGateway,
  paymentPlan,
}: AcceptedPaymentPlanHeaderButtonsProps): React.ReactElement {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const { isActiveProgram } = useProgramContext();

  const [mutateExport, { loading: loadingExport }] =
    useExportXlsxPpListPerFspMutation();

  const {
    mutatePaymentPlanAction: sendToPaymentGateway,
    loading: LoadingSendToPaymentGateway,
  } = usePaymentPlanAction(Action.SendToPaymentGateway, paymentPlan.id, () =>
    showMessage(t('Sending to Payment Gateway started')),
  );

  const shouldDisableExportXlsx =
    loadingExport ||
    !paymentPlan.hasFspDeliveryMechanismXlsxTemplate ||
    !canExportXlsx ||
    paymentPlan?.backgroundActionStatus ===
      PaymentPlanBackgroundActionStatus.XlsxExporting ||
    !isActiveProgram;

  return (
    <Box display="flex" alignItems="center">
      <>
        {paymentPlan.canCreateFollowUp && (
          <Box p={2}>
            <CreateFollowUpPaymentPlan paymentPlan={paymentPlan} />
          </Box>
        )}
        {!paymentPlan.hasPaymentListExportFile && (
          <Box p={2}>
            <LoadingButton
              loading={loadingExport}
              disabled={shouldDisableExportXlsx}
              color="primary"
              variant="contained"
              startIcon={<GetApp />}
              data-cy="button-export-xlsx"
              onClick={async () => {
                try {
                  await mutateExport({
                    variables: {
                      paymentPlanId: paymentPlan.id,
                    },
                  });
                  showMessage(t('Exporting XLSX started'));
                } catch (e) {
                  e.graphQLErrors.map((x) => showMessage(x.message));
                }
              }}
            >
              {t('Export Xlsx')}
            </LoadingButton>
          </Box>
        )}
        {paymentPlan.hasPaymentListExportFile && (
          <Box m={2}>
            <Button
              color="primary"
              component="a"
              variant="contained"
              data-cy="button-download-xlsx"
              download
              href={`/api/download-payment-plan-payment-list/${paymentPlan.id}`}
              disabled={
                !paymentPlan.hasFspDeliveryMechanismXlsxTemplate ||
                !canDownloadXlsx
              }
            >
              {t('Download XLSX')}
            </Button>
          </Box>
        )}
        <Box m={2}>
          <Button
            type="button"
            color="primary"
            variant="contained"
            onClick={() => sendToPaymentGateway()}
            data-cy="button-send-to-payment-gateway"
            disabled={!canSendToPaymentGateway || LoadingSendToPaymentGateway}
          >
            {t('Send to FSP')}
          </Button>
        </Box>
      </>
    </Box>
  );
}
