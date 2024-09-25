import { PaymentPlanQuery } from '@generated/graphql';
import { useTranslation } from 'react-i18next';
import { Grid } from '@mui/material';
import {
  SummaryBorder,
  SummaryValue,
} from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsResults/Styles';
import { LabelizedField } from '@core/LabelizedField';
import * as React from 'react';

interface ResultsForPeopleProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export const ResultsForPeople = ({ paymentPlan }: ResultsForPeopleProps) => {
  const { t } = useTranslation();
  const { totalHouseholdsCount } = paymentPlan;

  return (
    <Grid item xs={4}>
      <Grid container spacing={0} justifyContent="flex-end">
        <Grid item>
          <SummaryBorder>
            <LabelizedField label={t('Total Number of People')}>
              <SummaryValue>{totalHouseholdsCount || '0'}</SummaryValue>
            </LabelizedField>
          </SummaryBorder>
        </Grid>
      </Grid>
    </Grid>
  );
};
