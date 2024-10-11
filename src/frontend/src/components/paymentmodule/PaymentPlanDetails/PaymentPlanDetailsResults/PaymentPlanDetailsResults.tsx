import { Grid, Typography } from '@mui/material';
import * as React from 'react';
import { Pie } from 'react-chartjs-2';
import { useTranslation } from 'react-i18next';
import { PaymentPlanQuery } from '@generated/graphql';
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

interface PaymentPlanDetailsResultsProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export const PaymentPlanDetailsResults = ({
  paymentPlan,
}: PaymentPlanDetailsResultsProps): React.ReactElement => {
  const { t } = useTranslation();
  const { isSocialDctType } = useProgramContext();
  const {
    femaleChildrenCount,
    maleChildrenCount,
    femaleAdultsCount,
    maleAdultsCount,
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
          <Grid item xs={4}>
            <Grid container spacing={3} justifyContent="flex-start">
              <Grid item xs={6}>
                <FieldBorder color={colors.femaleChildren}>
                  <LabelizedField
                    label={t('Female Children')}
                    value={femaleChildrenCount}
                  />
                </FieldBorder>
              </Grid>
              <Grid item xs={6}>
                <FieldBorder color={colors.femaleAdult}>
                  <LabelizedField
                    label={t('Female Adults')}
                    value={femaleAdultsCount}
                  />
                </FieldBorder>
              </Grid>
              <Grid item xs={6}>
                <FieldBorder color={colors.maleChildren}>
                  <LabelizedField
                    label={t('Male Children')}
                    value={maleChildrenCount}
                  />
                </FieldBorder>
              </Grid>
              <Grid item xs={6}>
                <FieldBorder color={colors.maleAdult}>
                  <LabelizedField
                    label={t('Male Adults')}
                    value={maleAdultsCount}
                  />
                </FieldBorder>
              </Grid>
            </Grid>
          </Grid>
          <Grid item xs={4}>
            <Grid
              container
              spacing={0}
              justifyContent="flex-start"
              alignItems="center"
            >
              <Grid item xs={4}>
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
                            femaleChildrenCount,
                            femaleAdultsCount,
                            maleChildrenCount,
                            maleAdultsCount,
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
