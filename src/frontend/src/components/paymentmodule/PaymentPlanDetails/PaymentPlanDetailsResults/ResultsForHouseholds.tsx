import { useTranslation } from 'react-i18next';
import { Grid } from '@mui/material';
import {
  SummaryBorder,
  SummaryValue,
} from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsResults/Styles';
import { LabelizedField } from '@core/LabelizedField';
import * as React from 'react';
import { PaymentPlanQuery } from '@generated/graphql';

interface ResultsForHouseholdsProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export const ResultsForHouseholds = ({
  paymentPlan,
}: ResultsForHouseholdsProps) => {
  const { t } = useTranslation();
  const { totalHouseholdsCount, totalIndividualsCount } = paymentPlan;

  return (
    <Grid item xs={4}>
      <Grid container spacing={0} justifyContent="flex-end">
        <Grid item xs={6}>
          <SummaryBorder>
            <LabelizedField label={t('Total Number of Households')}>
              <SummaryValue>{totalHouseholdsCount || '0'}</SummaryValue>
            </LabelizedField>
          </SummaryBorder>
        </Grid>
        <Grid item xs={6}>
          <SummaryBorder>
            <LabelizedField label={t('Targeted Individuals')}>
              <SummaryValue>{totalIndividualsCount || '0'}</SummaryValue>
            </LabelizedField>
          </SummaryBorder>
        </Grid>
      </Grid>
    </Grid>
  );
};
