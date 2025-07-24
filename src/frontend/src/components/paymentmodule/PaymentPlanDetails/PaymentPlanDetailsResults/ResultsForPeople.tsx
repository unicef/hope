import { useTranslation } from 'react-i18next';
import { Grid2 as Grid } from '@mui/material';
import {
  SummaryBorder,
  SummaryValue,
} from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsResults/Styles';
import { LabelizedField } from '@core/LabelizedField';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';

interface ResultsForPeopleProps {
  paymentPlan: PaymentPlanDetail;
}

export const ResultsForPeople = ({ paymentPlan }: ResultsForPeopleProps) => {
  const { t } = useTranslation();
  const { totalHouseholdsCount } = paymentPlan;

  return (
    <Grid size={{ xs: 4 }}>
      <Grid container spacing={0} justifyContent="flex-end">
        <Grid>
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
