import { Button } from '@material-ui/core';
import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { PaymentPlanQuery } from '../../../__generated__/graphql';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { BaseSection } from '../../core/BaseSection';
import { Missing } from '../../core/Missing';

interface PaymentInstructionsSectionProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export const PaymentInstructionsSection = ({
  paymentPlan,
}: PaymentInstructionsSectionProps): ReactElement => {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();

  const buttons = (
    <Button
      component={Link}
      to={`/${baseUrl}/payment-module/payment-plans/${paymentPlan.id}/setup-payment-instructions/create`}
      variant='outlined'
      color='primary'
    >
      {t('Set up Payment Instructions')}
    </Button>
  );
  return (
    <BaseSection title='Set up Payment Instructions' buttons={buttons}>
      <>
        <Missing />
      </>
    </BaseSection>
  );
};
