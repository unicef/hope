import { Box, Button } from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { PaymentPlanQuery } from '../../../../../__generated__/graphql';

const ButtonContainer = styled.span`
  margin: 0 ${({ theme }) => theme.spacing(2)}px;
`;

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
  const [openDuplicate, setOpenDuplicate] = useState(false);
  const [openDelete, setOpenDelete] = useState(false);
  return (
    <Box display='flex' alignItems='center'>
      {canDownloadXlsx && (
        <ButtonContainer>
          <Button
            variant='contained'
            color='primary'
            onClick={() => setOpenApprove(true)}
          >
            {t('Download XLSX')}
          </Button>
        </ButtonContainer>
      )}
      {canSendToFsp && (
        <ButtonContainer>
          <Button
            variant='contained'
            color='primary'
            onClick={() => setOpenApprove(true)}
          >
            {t('Send to Fsp')}
          </Button>
        </ButtonContainer>
      )}
    </Box>
  );
};
