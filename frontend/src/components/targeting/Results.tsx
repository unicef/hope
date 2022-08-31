import { Grid, Typography } from '@material-ui/core';
import React from 'react';
import { Pie } from 'react-chartjs-2';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { MiśTheme } from '../../theme';
import {
  TargetPopulationBuildStatus,
  TargetPopulationQuery,
} from '../../__generated__/graphql';
import { LabelizedField } from '../core/LabelizedField';
import { PaperContainer } from './PaperContainer';

const colors = {
  femaleChildren: '#5F02CF',
  maleChildren: '#1D6A64',
  femaleAdult: '#DFCCF5',
  maleAdult: '#B1E3E0',
};

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(2)}px;
`;

const ContentWrapper = styled.div`
  display: flex;
`;

const FieldBorder = styled.div`
  padding: 0 ${({ theme }) => theme.spacing(2)}px;
  border-color: ${(props) => props.color};
  border-left-width: 2px;
  border-left-style: solid;
`;

const SummaryBorder = styled.div`
  padding: ${({ theme }) => theme.spacing(4)}px;
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
  margin-top: ${({ theme }) => theme.spacing(2)}px;
`;

const ChartContainer = styled.div`
  width: 100px;
  height: 100px;
  margin: 0 auto;
`;


interface ResultsProps {
  targetPopulation: TargetPopulationQuery['targetPopulation'];
}

export function Results({
  targetPopulation,
}: ResultsProps): React.ReactElement {
  const { t } = useTranslation();
  if (targetPopulation.buildStatus !== TargetPopulationBuildStatus.Ok) {
    return null;
  }
  return (
    <div>
      <PaperContainer>
        <Title>
          <Typography variant='h6'>{t('Results')}</Typography>
        </Title>
        <ContentWrapper>
          <>
            <Grid container spacing={0} justify='flex-start'>
              <Grid item xs={6}>
                <FieldBorder color={colors.femaleChildren}>
                  <LabelizedField
                    label={t('Female Children')}
                    value={targetPopulation.childFemaleCount}
                  />
                </FieldBorder>
              </Grid>
              <Grid item xs={6}>
                <FieldBorder color={colors.femaleAdult}>
                  <LabelizedField
                    label={t('Female Adults')}
                    value={targetPopulation.adultFemaleCount}
                  />
                </FieldBorder>
              </Grid>
              <Grid item xs={6}>
                <FieldBorder color={colors.maleChildren}>
                  <LabelizedField
                    label={t('Male Children')}
                    value={targetPopulation.childMaleCount}
                  />
                </FieldBorder>
              </Grid>
              <Grid item xs={6}>
                <FieldBorder color={colors.maleAdult}>
                  <LabelizedField
                    label={t('Male Adults')}
                    value={targetPopulation.adultMaleCount}
                  />
                </FieldBorder>
              </Grid>
            </Grid>
            <Grid
              container
              spacing={0}
              justify='flex-start'
              alignItems='center'
            >
              <Grid item xs={4}>
                <ChartContainer>
                  <Pie
                    width={100}
                    height={100}
                    options={{
                      legend: {
                        display: false,
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
                            targetPopulation.childFemaleCount,
                            targetPopulation.adultFemaleCount,
                            targetPopulation.childMaleCount,
                            targetPopulation.childFemaleCount,
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
            <Grid container spacing={0} justify='flex-end'>
              <SummaryBorder>
                <LabelizedField label={t('Total Number of Households')}>
                  <SummaryValue>
                    {targetPopulation.totalHouseholdsCount || '0'}
                  </SummaryValue>
                </LabelizedField>
              </SummaryBorder>
              <SummaryBorder>
                <LabelizedField label={t('Targeted Individuals')}>
                  <SummaryValue>
                    {targetPopulation.totalIndividualsCount || '0'}
                  </SummaryValue>
                </LabelizedField>
              </SummaryBorder>
            </Grid>
          </>
        </ContentWrapper>
      </PaperContainer>
    </div>
  );
}
