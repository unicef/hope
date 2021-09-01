import { Grid, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { MiśTheme } from '../../theme';
import { choicesToDict, programStatusToColor } from '../../utils/utils';
import {
  ProgrammeChoiceDataQuery,
  ProgramNode,
} from '../../__generated__/graphql';
import { ContainerColumnWithBorder } from '../ContainerColumnWithBorder';
import { LabelizedField } from '../LabelizedField';
import { OverviewContainer } from '../OverviewContainer';
import { StatusBox } from '../StatusBox';
import { UniversalMoment } from '../UniversalMoment';

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;

const NumberOfHouseHolds = styled.div`
  padding: ${({ theme }) => theme.spacing(8)}px;
  border-color: #b1b1b5;
  border-left-width: 1px;
  border-left-style: solid;
`;
const NumberOfHouseHoldsValue = styled.div`
  font-family: ${({ theme }: { theme: MiśTheme }) =>
    theme.hctTypography.fontFamily};
  color: #253b46;
  font-size: 36px;
  line-height: 32px;
  margin-top: ${({ theme }) => theme.spacing(2)}px;
`;

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

interface ProgramDetailsProps {
  program: ProgramNode;
  choices: ProgrammeChoiceDataQuery;
}

export function ProgramDetails({
  program,
  choices,
}: ProgramDetailsProps): React.ReactElement {
  const { t } = useTranslation();
  const {
    programFrequencyOfPaymentsChoices,
    programSectorChoices,
    programScopeChoices,
  } = choices;
  const programFrequencyOfPaymentsChoicesDict = choicesToDict(
    programFrequencyOfPaymentsChoices,
  );
  const programSectorChoicesDict = choicesToDict(programSectorChoices);
  const programScopeChoicesDict = choicesToDict(programScopeChoices);
  return (
    <ContainerColumnWithBorder data-cy='program-details-container'>
      <Title>
        <Typography variant='h6'>{t('Programme Details')}</Typography>
      </Title>
      <OverviewContainer>
        <Grid container spacing={6}>
          <Grid item xs={4}>
            <LabelizedField label={t('status')}>
              <StatusContainer>
                <StatusBox
                  status={program.status}
                  statusToColor={programStatusToColor}
                />
              </StatusContainer>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField
              label={t('START DATE')}
              value={<UniversalMoment>{program.startDate}</UniversalMoment>}
            />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField
              label={t('END DATE')}
              value={<UniversalMoment>{program.endDate}</UniversalMoment>}
            />
          </Grid>

          <Grid item xs={4}>
            <LabelizedField
              label={t('Sector')}
              value={programSectorChoicesDict[program.sector]}
            />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField
              label={t('Scope')}
              value={programScopeChoicesDict[program.scope]}
            />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField
              label={t('Frequency of Payment')}
              value={
                programFrequencyOfPaymentsChoicesDict[
                  program.frequencyOfPayments
                ]
              }
            />
          </Grid>

          <Grid item xs={4}>
            <LabelizedField
              label={t('Administrative Areas of implementation')}
              value={program.administrativeAreasOfImplementation}
            />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField
              label={t('Description')}
              value={program.description}
            />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField
              label={t('CASH+')}
              value={program.cashPlus ? t('Yes') : t('No')}
            />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField
              label={t(
                'Does this programme use individuals’ data for targeting or entitlement calculation?',
              )}
              value={program.individualDataNeeded ? t('Yes') : t('No')}
            />
          </Grid>
        </Grid>
        <NumberOfHouseHolds>
          <LabelizedField label={t('Total Number of Households')}>
            <NumberOfHouseHoldsValue>
              {program.totalNumberOfHouseholds}
            </NumberOfHouseHoldsValue>
          </LabelizedField>
        </NumberOfHouseHolds>
      </OverviewContainer>
    </ContainerColumnWithBorder>
  );
}
