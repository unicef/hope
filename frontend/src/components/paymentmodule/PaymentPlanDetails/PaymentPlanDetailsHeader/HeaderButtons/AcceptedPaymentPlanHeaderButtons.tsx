import { Box, Button } from '@material-ui/core';
import { GetApp } from '@material-ui/icons';
import styled from 'styled-components';
import React from 'react';
import { useTranslation } from 'react-i18next';
import {
  PaymentPlanQuery,
  useExportXlsxPpListPerFspMutation,
} from '../../../../../__generated__/graphql';
import { LoadingButton } from '../../../../core/LoadingButton';
import { useSnackbar } from '../../../../../hooks/useSnackBar';
import { ImportXlsxPaymentPlanPaymentListPerFsp } from '../../ImportXlsxPaymentPlanPaymentListPerFsp';

const DownloadIcon = styled(GetApp)`
  color: #043f91;
`;

export interface AcceptedPaymentPlanHeaderButtonsProps {
  canDownloadXlsx: boolean;
  canSendToFsp: boolean;
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export const AcceptedPaymentPlanHeaderButtons = ({
  canDownloadXlsx,
  canSendToFsp,
  paymentPlan,
}: AcceptedPaymentPlanHeaderButtonsProps): React.ReactElement => {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const [
    mutateExport,
    { loading: loadingExport },
  ] = useExportXlsxPpListPerFspMutation();

  return (
    <Box display='flex' alignItems='center'>
      {canDownloadXlsx && (
        <>
          {!paymentPlan.hasPaymentListPerFspZipFile ? (
            <Box p={2}>
              <LoadingButton
                loading={loadingExport}
                disabled={loadingExport}
                color='primary'
                variant='contained'
                startIcon={<GetApp />}
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
          ) : (
            <Box m={2}>
              <Button
                color='primary'
                component='a'
                variant='contained'
                download
                href={`/api/download-payment-plan-payment-list-per-fsp/${paymentPlan.id}`}
              >
                {t('Download XLSX')}
              </Button>
            </Box>
          )}
        </>
      )}
      {canSendToFsp && (
        <Box m={2}>
          {/*TODO: connect this button*/}
          <Button color='primary' variant='contained'>
            {t('Send to FSP')}
          </Button>
        </Box>
      )}
    </Box>
  );
};
