import { Box, Button } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { ButtonTooltip } from '../../../core/ButtonTooltip';
import { Link, useLocation } from 'react-router-dom';

interface SetUpFspButtonActionsProps {
  step: number;
  submitForm: (values) => void;
  businessArea: string;
  paymentPlanId: string;
  handleBackStep: () => void;
  isFspEmpty: boolean;
}

export const SetUpFspButtonActions = ({
  step,
  submitForm,
  businessArea,
  paymentPlanId,
  handleBackStep,
  isFspEmpty,
}: SetUpFspButtonActionsProps): React.ReactElement => {
  const { t } = useTranslation();
  const location = useLocation();
  const isFollowUp = location.pathname.indexOf('followup') !== -1;

  return (
    <Box pt={3} display='flex'>
      <Box mr={3}>
        {step === 0 && (
          <ButtonTooltip
            component={Link}
            title={t('All delivery mechanisms must have a FSP assigned')}
            disabled={isFspEmpty}
            to={`/${businessArea}/payment-module/${
              isFollowUp ? 'followup-payment-plans' : 'payment-plans'
            }/${paymentPlanId}`}
          >
            {t('Cancel')}
          </ButtonTooltip>
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
