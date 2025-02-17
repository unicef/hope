import { Grid2 as Grid } from '@mui/material';
import {
  SummaryBorder,
  SummaryValue,
} from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsResults/Styles';
import { LabelizedField } from '@core/LabelizedField';
import { PaymentPlanQuery } from '@generated/graphql';
import { useProgramContext } from 'src/programContext';

interface ResultsForHouseholdsProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export const ResultsForHouseholds = ({
  paymentPlan,
}: ResultsForHouseholdsProps) => {
  const { totalHouseholdsCount, totalIndividualsCount } = paymentPlan;
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  return (
    <Grid size={{ xs: 4 }}>
      <Grid container spacing={0} justifyContent="flex-end">
        <Grid size={{ xs:6 }}>
          <SummaryBorder>
            <LabelizedField
              label={`Total Number of ${beneficiaryGroup?.groupLabelPlural}`}
            >
              <SummaryValue>{totalHouseholdsCount || '0'}</SummaryValue>
            </LabelizedField>
          </SummaryBorder>
        </Grid>
        <Grid size={{ xs:6 }}>
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
