import { Box, Button } from '@mui/material';
import { EditRounded } from '@mui/icons-material';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { PaymentPlanQuery } from '@generated/graphql';
import { DeletePaymentPlan } from '../DeletePaymentPlan';
import { LockPaymentPlan } from '../LockPaymentPlan';
import { useProgramContext } from '../../../../../programContext';

export interface OpenPaymentPlanHeaderButtonsProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
  canRemove: boolean;
  canEdit: boolean;
  canLock: boolean;
}

export function OpenPaymentPlanHeaderButtons({
  paymentPlan,
  canRemove,
  canEdit,
  canLock,
}: OpenPaymentPlanHeaderButtonsProps): React.ReactElement {
  const { t } = useTranslation();
  const { isActiveProgram } = useProgramContext();

  return (
    <Box display="flex" alignItems="center">
      {canRemove && <DeletePaymentPlan paymentPlan={paymentPlan} />}
      {canEdit && (
        <Box m={2}>
          <Button
            variant="outlined"
            color="primary"
            startIcon={<EditRounded />}
            data-cy="button-edit-payment-plan"
            component={Link}
            to={'./edit'}
            disabled={!isActiveProgram}
          >
            {t('Edit')}
          </Button>
        </Box>
      )}
      {canLock && (
        <Box m={2}>
          <LockPaymentPlan paymentPlan={paymentPlan} />
        </Box>
      )}
    </Box>
  );
}
