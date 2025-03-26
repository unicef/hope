import { Box, Button } from '@mui/material';
import { EditRounded } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { DeletePaymentPlan } from '../DeletePaymentPlan';
import { LockPaymentPlan } from '../LockPaymentPlan';
import { useProgramContext } from '../../../../../programContext';
import { ReactElement } from 'react';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';

export interface OpenPaymentPlanHeaderButtonsProps {
  paymentPlan: PaymentPlanDetail;
  canRemove: boolean;
  canEdit: boolean;
  canLock: boolean;
}

export function OpenPaymentPlanHeaderButtons({
  paymentPlan,
  canRemove,
  canEdit,
  canLock,
}: OpenPaymentPlanHeaderButtonsProps): ReactElement {
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
