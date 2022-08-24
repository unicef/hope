import { Box, Button } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

interface SetUpFspButtonActionsProps {
  step: number;
  submitForm: (values) => void;
  businessArea: string;
  paymentPlanId: string;
  handleBackStep: () => void;
}

export const SetUpFspButtonActions = ({
  step,
  submitForm,
  businessArea,
  paymentPlanId,
  handleBackStep,
}: SetUpFspButtonActionsProps): React.ReactElement => {
  const { t } = useTranslation();

  return (
    <Box pt={3} display='flex'>
      <Box mr={3}>
        {step === 0 && (
          <Button
            component={Link}
            to={`/${businessArea}/payment-module/payment-plan/${paymentPlanId}`}
          >
            {t('Cancel')}
          </Button>
        )}
        {step === 1 && <Button onClick={handleBackStep}>{t('Back')}</Button>}
      </Box>
      <Button variant='contained' color='primary' onClick={submitForm}>
        {t(step === 0 ? 'Next' : 'Save')}
      </Button>
    </Box>
  );
};
