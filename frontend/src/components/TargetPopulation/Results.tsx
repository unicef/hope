import React from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { Typography, Paper, Grid } from '@material-ui/core';
import { Pie } from 'react-chartjs-2';
import { MiśTheme } from '../../theme';
import { LabelizedField } from '../LabelizedField';
import { TargetPopulationQuery } from '../../__generated__/graphql';

const colors = {
  femaleChildren: '#023E90',
  maleChildren: '#029BFE',
  femaleAdult: '#73C302',
  maleAdult: '#F2E82C',
};

const PaperContainer = styled(Paper)`
  padding: ${({ theme }) => theme.spacing(3)}px
    ${({ theme }) => theme.spacing(4)}px;
  margin: ${({ theme }) => theme.spacing(5)}px;
  border-bottom: 1px solid rgba(224, 224, 224, 1);
`;

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

const Label = styled.p`
  color: #b1b1b5;
`;

interface ResultsProps {
  resultsData?:
    | TargetPopulationQuery['targetPopulation']['candidateStats']
    | TargetPopulationQuery['targetPopulation']['finalStats'];
  totalNumOfHouseholds?;
  totalNumOfIndividuals?;
}

export function Results({
  resultsData,
  totalNumOfHouseholds,
  totalNumOfIndividuals,
}: ResultsProps) {
  const { t } = useTranslation();

  return (
    <div>
      <PaperContainer>
        <Title>
          <Typography variant='h6'>{t('Results')}</Typography>
        </Title>
        <ContentWrapper>
          {resultsData ? (
            <>
              <Grid container spacing={0} justify='flex-start'>
                <Grid item xs={6}>
                  <FieldBorder color={colors.femaleChildren}>
                    <LabelizedField
                      label='Female Children'
                      value={resultsData.childFemale}
                    />
                  </FieldBorder>
                </Grid>
                <Grid item xs={6}>
                  <FieldBorder color={colors.femaleAdult}>
                    <LabelizedField
                      label='Female Adults'
                      value={resultsData.adultFemale}
                    />
                  </FieldBorder>
                </Grid>
                <Grid item xs={6}>
                  <FieldBorder color={colors.maleChildren}>
                    <LabelizedField
                      label='Male Children'
                      value={resultsData.childMale}
                    />
                  </FieldBorder>
                </Grid>
                <Grid item xs={6}>
                  <FieldBorder color={colors.maleAdult}>
                    <LabelizedField
                      label='Male Adults'
                      value={resultsData.adultMale}
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
                          'Female Children',
                          'Female Adults',
                          'Male Children',
                          'Male Adults',
                        ],
                        datasets: [
                          {
                            data: [
                              resultsData.childFemale,
                              resultsData.adultFemale,
                              resultsData.childMale,
                              resultsData.adultMale,
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
                  <LabelizedField label='Total Number of Households'>
                    <SummaryValue>{totalNumOfHouseholds || '0'}</SummaryValue>
                  </LabelizedField>
                </SummaryBorder>
                <SummaryBorder>
                  <LabelizedField label='Targeted Individuals'>
                    <SummaryValue>
                      {totalNumOfIndividuals || '0'}
                    </SummaryValue>
                  </LabelizedField>
                </SummaryBorder>
              </Grid>
            </>
          ) : (
            <Label>Add targeting criteria to see results.</Label>
          )}
        </ContentWrapper>
      </PaperContainer>
    </div>
  );
}
