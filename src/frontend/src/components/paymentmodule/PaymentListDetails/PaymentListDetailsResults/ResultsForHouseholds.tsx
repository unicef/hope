import { Grid } from '@mui/material';
import {
  SummaryBorder,
  SummaryValue,
} from '@components/paymentmodule/PaymentListDetails/PaymentListDetailsResults/Styles';
import { LabelizedField } from '@core/LabelizedField';
import { useProgramContext } from 'src/programContext';
import type { PaymentListDetail } from '@restgenerated/models/PaymentListDetail';
import { responsiveGridSize } from 'src/responsive';

interface ResultsForHouseholdsProps {
  paymentList: PaymentListDetail;
}

export const ResultsForHouseholds = ({
  paymentList,
}: ResultsForHouseholdsProps) => {
  const { totalHouseholdsCount, totalIndividualsCount } = paymentList;
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  return (
    <Grid size={responsiveGridSize('third')}>
      <Grid
        container
        spacing={0}
        sx={{
          justifyContent: 'flex-end',
        }}
      >
        <Grid size={{ xs: 6 }}>
          <SummaryBorder>
            <LabelizedField
              label={`Total Number of ${beneficiaryGroup?.groupLabelPlural}`}
            >
              <SummaryValue>{totalHouseholdsCount || '0'}</SummaryValue>
            </LabelizedField>
          </SummaryBorder>
        </Grid>
        <Grid size={{ xs: 6 }}>
          <SummaryBorder>
            <LabelizedField
              label={`Targeted ${beneficiaryGroup?.memberLabelPlural}`}
            >
              <SummaryValue>{totalIndividualsCount || '0'}</SummaryValue>
            </LabelizedField>
          </SummaryBorder>
        </Grid>
      </Grid>
    </Grid>
  );
};
