import { Grid2 as Grid, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { MiśTheme } from '../../theme';
import { LabelizedField } from '@core/LabelizedField';
import { PaperContainer } from './PaperContainer';
import { FieldBorder } from '@core/FieldBorder';
import { Pie } from 'react-chartjs-2';
import { ReactElement } from 'react';
import { PaymentPlanBuildStatus, PaymentPlanQuery } from '@generated/graphql';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';

const colors = {
  femaleChildren: '#5F02CF',
  maleChildren: '#1D6A64',
  femaleAdult: '#DFCCF5',
  maleAdult: '#B1E3E0',
};

const ChartContainer = styled.div`
  width: 100px;
  height: 100px;
  margin: 0 auto;
`;

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(2)};
`;

const ContentWrapper = styled.div`
  display: flex;
`;

const SummaryBorder = styled.div`
  padding: ${({ theme }) => theme.spacing(4)};
  border-color: #b1b1b5;
  border-left-width: 1px;
  border-left-style: solid;
`;

const SummaryValue = styled.div`
  font-family: ${({ theme }: { theme: MiśTheme }) =>
    theme.hctTypography.fontFamily};
  color: #253b46;
  font-size: 36px;
  line-height: 32px;
  margin-top: ${({ theme }) => theme.spacing(2)};
`;

interface ResultsProps {
  targetPopulation: PaymentPlanDetail;
}

function ResultsForPeople({ targetPopulation }: ResultsProps): ReactElement {
  const { t } = useTranslation();
  if (targetPopulation.build_status !== PaymentPlanBuildStatus.Ok) {
    return null;
  }
  return (
    <div>
      <PaperContainer>
        <Title>
          <Typography variant="h6">{t('Results')}</Typography>
        </Title>
        <ContentWrapper>
          <Grid container>
            <Grid size={{ xs: 4 }}>
              <Grid container spacing={0} justifyContent="flex-start">
                <Grid size={{ xs: 6 }}>
                  <FieldBorder color={colors.femaleChildren}>
                    <LabelizedField
                      label={t('Female Children')}
                      value={targetPopulation.femaleChildrenCount}
                    />
                  </FieldBorder>
                </Grid>
                <Grid size={{ xs: 6 }}>
                  <FieldBorder color={colors.femaleAdult}>
                    <LabelizedField
                      label={t('Female Adults')}
                      value={targetPopulation.femaleAdultsCount}
                    />
                  </FieldBorder>
                </Grid>
                <Grid size={{ xs: 6 }}>
                  <FieldBorder color={colors.maleChildren}>
                    <LabelizedField
                      label={t('Male Children')}
                      value={targetPopulation.maleChildrenCount}
                    />
                  </FieldBorder>
                </Grid>
                <Grid size={{ xs: 6 }}>
                  <FieldBorder color={colors.maleAdult}>
                    <LabelizedField
                      label={t('Male Adults')}
                      value={targetPopulation.maleAdultsCount}
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
                  <ChartContainer>
                    <Pie
                      width={100}
                      height={100}
                      options={{
                        plugins: {
                          legend: {
                            display: false,
                          },
                        },
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
                              targetPopulation.femaleChildrenCount,
                              targetPopulation.femaleAdultsCount,
                              targetPopulation.maleChildrenCount,
                              targetPopulation.maleAdultsCount,
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
            <Grid size={{ xs: 4 }}>
              <Grid container spacing={0} justifyContent="flex-end">
                <Grid size={{ xs: 6 }}>
                  <SummaryBorder>
                    <LabelizedField label={t('Total Number of People')}>
                      <SummaryValue>
                        {targetPopulation.totalHouseholdsCount || '0'}
                      </SummaryValue>
                    </LabelizedField>
                  </SummaryBorder>
                </Grid>
              </Grid>
            </Grid>
          </Grid>
        </ContentWrapper>
      </PaperContainer>
    </div>
  );
}

export default withErrorBoundary(ResultsForPeople, 'ResultsForPeople');
