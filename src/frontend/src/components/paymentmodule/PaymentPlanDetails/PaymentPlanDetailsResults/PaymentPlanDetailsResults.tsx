import { Grid2 as Grid, Typography } from '@mui/material';
import { Pie } from 'react-chartjs-2';
import { useTranslation } from 'react-i18next';
import { LabelizedField } from '@core/LabelizedField';
import { PaperContainer } from '../../../targeting/PaperContainer';
import { FieldBorder } from '@core/FieldBorder';
import { useProgramContext } from '../../../../programContext';
import {
  ChartContainer,
  colors,
  ContentWrapper,
  Title,
} from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsResults/Styles';
import { ResultsForHouseholds } from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsResults/ResultsForHouseholds';
import { ResultsForPeople } from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsResults/ResultsForPeople';
import { ReactElement } from 'react';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';

interface PaymentPlanDetailsResultsProps {
  paymentPlan: PaymentPlanDetail;
}

export const PaymentPlanDetailsResults = ({
  paymentPlan,
}: PaymentPlanDetailsResultsProps): ReactElement => {
  const { t } = useTranslation();
  const { isSocialDctType } = useProgramContext();
  const {
    female_children_count,
    male_children_count,
    female_adults_count,
    male_adults_count,
  } = paymentPlan;

  const ResultsComponent = isSocialDctType
    ? ResultsForPeople
    : ResultsForHouseholds;

  return (
    <PaperContainer>
      <Title>
        <Typography variant="h6">{t('Results')}</Typography>
      </Title>
      <ContentWrapper>
        <Grid container>
          <Grid size={{ xs: 4 }}>
            <Grid container spacing={3} justifyContent="flex-start">
              <Grid size={{ xs: 6 }}>
                <FieldBorder color={colors.femaleChildren}>
                  <LabelizedField
                    label={t('Female Children')}
                    value={female_children_count}
                  />
                </FieldBorder>
              </Grid>
              <Grid size={{ xs: 6 }}>
                <FieldBorder color={colors.femaleAdult}>
                  <LabelizedField
                    label={t('Female Adults')}
                    value={female_adults_count}
                  />
                </FieldBorder>
              </Grid>
              <Grid size={{ xs: 6 }}>
                <FieldBorder color={colors.maleChildren}>
                  <LabelizedField
                    label={t('Male Children')}
                    value={male_children_count}
                  />
                </FieldBorder>
              </Grid>
              <Grid size={{ xs: 6 }}>
                <FieldBorder color={colors.maleAdult}>
                  <LabelizedField
                    label={t('Male Adults')}
                    value={male_adults_count}
                  />
                </FieldBorder>
              </Grid>
            </Grid>
          </Grid>
          <Grid size={{ xs: 4 }}>
            <Grid
              container
              spacing={0}
              justifyContent="flex-start"
              alignItems="center"
            >
              <Grid size={{ xs: 4 }}>
                <ChartContainer data-cy="chart-container">
                  <Pie
                    width={100}
                    height={100}
                    options={{
                      plugins: {
                        legend: {
                          display: false,
                        },
                      },
                      responsive: true,
                      maintainAspectRatio: false,
                    }}
                    data={{
                      labels: [
                        t('Female Children'),
                        t('Female Adults'),
                        t('Male Children'),
                        t('Male Adults'),
                      ],
                      datasets: [
                        {
                          data: [
                            female_children_count,
                            female_adults_count,
                            male_children_count,
                            male_adults_count,
                          ],
                          backgroundColor: [
                            colors.femaleChildren,
                            colors.femaleAdult,
                            colors.maleChildren,
                            colors.maleAdult,
                          ],
                        },
                      ],
                    }}
                  />
                </ChartContainer>
              </Grid>
            </Grid>
          </Grid>
          <ResultsComponent paymentPlan={paymentPlan} />
        </Grid>
      </ContentWrapper>
    </PaperContainer>
  );
};
