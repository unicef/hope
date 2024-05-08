import { Grid, Typography } from '@mui/material';
import * as React from 'react';
import { Pie } from 'react-chartjs-2';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import {
  TargetPopulationBuildStatus,
  TargetPopulationQuery,
} from '@generated/graphql';
import { MiśTheme } from '../../theme';
import { FieldBorder } from '@core/FieldBorder';
import { LabelizedField } from '@core/LabelizedField';
import { PaperContainer } from './PaperContainer';

const colors = {
  femaleChildren: '#5F02CF',
  maleChildren: '#1D6A64',
  femaleAdult: '#DFCCF5',
  maleAdult: '#B1E3E0',
};

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

const ChartContainer = styled.div`
  width: 100px;
  height: 100px;
  margin: 0 auto;
`;

interface ResultsProps {
  targetPopulation: TargetPopulationQuery['targetPopulation'];
}

export function ResultsForPeople({
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
          <Typography variant="h6">{t('Results')}</Typography>
        </Title>
        <ContentWrapper>
          <Grid container>
            <Grid item xs={4}>

            </Grid>
            <Grid item xs={4}>

            </Grid>
            <Grid item xs={4}>
              <Grid container spacing={0} justifyContent="flex-end">
                <Grid item xs={6}>
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
