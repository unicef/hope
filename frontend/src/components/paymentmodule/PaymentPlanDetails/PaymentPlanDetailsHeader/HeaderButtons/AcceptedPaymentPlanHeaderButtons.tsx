import { Box, Button } from '@material-ui/core';
import { GetApp } from '@material-ui/icons';
import styled from 'styled-components';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { PaymentPlanQuery } from '../../../../../__generated__/graphql';

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
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [openApprove, setOpenApprove] = useState(false);

  return (
    <Box display='flex' alignItems='center'>
      {canDownloadXlsx && (
        <Box m={2}>
          <Button
            color='primary'
            startIcon={<DownloadIcon />}
            component='a'
            download
            href={`/api/download-payment-plan-payment-list-per-fsp/${paymentPlan.id}`}
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
