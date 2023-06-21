import { Box, Button } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useLocation } from 'react-router-dom';

interface SetUpFspButtonActionsProps {
  step: number;
  submitForm: (values) => void;
  baseUrl: string;
  paymentPlanId: string;
  handleBackStep: () => void;
}

export const SetUpFspButtonActions = ({
  step,
  submitForm,
  baseUrl,
  paymentPlanId,
  handleBackStep,
}: SetUpFspButtonActionsProps): React.ReactElement => {
  const { t } = useTranslation();
  const location = useLocation();
  const isFollowUp = location.pathname.indexOf('followup') !== -1;

  return (
    <Box pt={3} display='flex'>
      <Box mr={3}>
        {step === 0 && (
          <Button
            component={Link}
            to={`/${baseUrl}/payment-module/${
              isFollowUp ? 'followup-payment-plans' : 'payment-plans'
            }/${paymentPlanId}`}
          >
            {t('Cancel')}
          </Button>
        )}
        {step === 1 && <Button onClick={handleBackStep}>{t('Back')}</Button>}
      </Box>
      <Button
        data-cy='button-next-save'
        variant='contained'
        color='primary'
        onClick={submitForm}
      >
        {t(step === 0 ? 'Next' : 'Save')}
      </Button>
    </Box>
  );
};
