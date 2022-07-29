import { Box, Button, IconButton } from '@material-ui/core';
import { FileCopy } from '@material-ui/icons';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { PaymentPlanQuery } from '../../../../../__generated__/graphql';

export interface LockedPaymentPlanHeaderButtonsProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
  canDuplicate: boolean;
  canLock: boolean;
  canSendForApproval: boolean;
}

export const LockedPaymentPlanHeaderButtons = ({
  paymentPlan,
  canDuplicate,
  canLock,
  canSendForApproval,
}: LockedPaymentPlanHeaderButtonsProps): React.ReactElement => {
  const { t } = useTranslation();
  const [openApprove, setOpenApprove] = useState(false);
  const [openDuplicate, setOpenDuplicate] = useState(false);
  const [openDelete, setOpenDelete] = useState(false);
  return (
    <Box display='flex' alignItems='center'>
      {canDuplicate && (
        <IconButton onClick={() => setOpenDuplicate(true)}>
          <FileCopy />
        </IconButton>
      )}
      {canLock && (
        <Box m={2}>
          <Button
            variant='outlined'
            color='primary'
            onClick={() => setOpenApprove(true)}
          >
            {t('Unlock')}
          </Button>
        </Box>
      )}
      {canSendForApproval && (
        <Box m={2}>
          <Button
            variant='contained'
            color='primary'
            onClick={() => setOpenApprove(true)}
          >
            {t('Send For Approval')}
          </Button>
        </Box>
      )}
    </Box>
  );
};
