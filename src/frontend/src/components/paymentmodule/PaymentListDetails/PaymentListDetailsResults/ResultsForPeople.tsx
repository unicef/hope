import { useTranslation } from 'react-i18next';
import { Grid } from '@mui/material';
import {
  SummaryBorder,
  SummaryValue,
} from '@components/paymentmodule/PaymentListDetails/PaymentListDetailsResults/Styles';
import { LabelizedField } from '@core/LabelizedField';
import type { PaymentListDetail } from '@restgenerated/models/PaymentListDetail';
import { responsiveGridSize } from 'src/responsive';

interface ResultsForPeopleProps {
  paymentList: PaymentListDetail;
}

export const ResultsForPeople = ({ paymentList }: ResultsForPeopleProps) => {
  const { t } = useTranslation();
  const { totalHouseholdsCount } = paymentList;

  return (
    <Grid size={responsiveGridSize('third')}>
      <Grid
        container
        spacing={0}
        sx={{
          justifyContent: 'flex-end',
        }}
      >
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
