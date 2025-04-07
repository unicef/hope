import { Grid2 as Grid } from '@mui/material';
import {
  SummaryBorder,
  SummaryValue,
} from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsResults/Styles';
import { LabelizedField } from '@core/LabelizedField';
import { useProgramContext } from 'src/programContext';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';

interface ResultsForHouseholdsProps {
  paymentPlan: PaymentPlanDetail;
}

export const ResultsForHouseholds = ({
  paymentPlan,
}: ResultsForHouseholdsProps) => {
  const { total_households_count, totalIndividualsCount } = paymentPlan;
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  return (
    <Grid size={{ xs: 4 }}>
      <Grid container spacing={0} justifyContent="flex-end">
        <Grid size={{ xs: 6 }}>
          <SummaryBorder>
            <LabelizedField
              label={`Total Number of ${beneficiaryGroup?.groupLabelPlural}`}
            >
              <SummaryValue>{total_households_count || '0'}</SummaryValue>
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
