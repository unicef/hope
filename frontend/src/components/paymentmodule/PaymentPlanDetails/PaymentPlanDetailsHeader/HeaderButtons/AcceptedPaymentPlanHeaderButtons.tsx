import { Box, Button } from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { PaymentPlanQuery } from '../../../../../__generated__/graphql';

export interface AcceptedPaymentPlanHeaderButtonsProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
  canDownloadXlsx: boolean;
  canSendToFsp: boolean;
}

export const AcceptedPaymentPlanHeaderButtons = ({
  paymentPlan,
  canDownloadXlsx,
  canSendToFsp,
}: AcceptedPaymentPlanHeaderButtonsProps): React.ReactElement => {
  const { t } = useTranslation();
  const [openApprove, setOpenApprove] = useState(false);

  return (
    <Box display='flex' alignItems='center'>
      {canDownloadXlsx && (
        <Box m={2}>
          <Button
            variant='contained'
            color='primary'
            onClick={() => setOpenApprove(true)}
          >
            {t('Download XLSX')}
          </Button>
        </Box>
      )}
      {canSendToFsp && (
        <Box m={2}>
          <Button
            variant='contained'
            color='primary'
            onClick={() => setOpenApprove(true)}
          >
            {t('Send to Fsp')}
          </Button>
        </Box>
      )}
    </Box>
  );
};
