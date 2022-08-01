import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Box, Button, IconButton } from '@material-ui/core';
import { EditRounded, Delete } from '@material-ui/icons';
import { useTranslation } from 'react-i18next';
import { LockPaymentPlan } from '../LockPaymentPlan';
import { PaymentPlanQuery } from '../../../../../__generated__/graphql';
import { useBusinessArea } from '../../../../../hooks/useBusinessArea';

export interface OpenPaymentPlanHeaderButtonsProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
  canRemove: boolean;
  canEdit: boolean;
  canLock: boolean;
}

export const OpenPaymentPlanHeaderButtons = ({
  paymentPlan,
  canRemove,
  canEdit,
  canLock,
}: OpenPaymentPlanHeaderButtonsProps): React.ReactElement => {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const [openLock, setOpenLock] = useState(false);
  const [openDelete, setOpenDelete] = useState(false);
  const { id } = paymentPlan;
  return (
    <Box display='flex' alignItems='center'>
      {canRemove && (
        <IconButton onClick={() => setOpenDelete(true)}>
          <Delete />
        </IconButton>
      )}
      {canEdit && (
        <Box m={2}>
          <Button
            variant='outlined'
            color='primary'
            startIcon={<EditRounded />}
            component={Link}
            to={`/${businessArea}/payment-module/payment-plans/${id}/edit`}
          >
            {t('Edit')}
          </Button>
        </Box>
      )}
      {canLock && (
        <Box m={2}>
          <LockPaymentPlan paymentPlanId={id} />
        </Box>
      )}
    </Box>
  );
};
