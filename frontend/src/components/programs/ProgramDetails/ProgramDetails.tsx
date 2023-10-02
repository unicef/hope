import { Grid, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import {
  ProgramQuery,
  ProgrammeChoiceDataQuery,
} from '../../../__generated__/graphql';
import { MiśTheme } from '../../../theme';
import { choicesToDict, programStatusToColor } from '../../../utils/utils';
import { ContainerColumnWithBorder } from '../../core/ContainerColumnWithBorder';
import { LabelizedField } from '../../core/LabelizedField';
import { Missing } from '../../core/Missing';
import { OverviewContainer } from '../../core/OverviewContainer';
import { StatusBox } from '../../core/StatusBox';
import { Title } from '../../core/Title';
import { UniversalMoment } from '../../core/UniversalMoment';

const NumberOfHouseHolds = styled.div`
  padding: ${({ theme }) => theme.spacing(4)}px;
  margin-left: ${({ theme }) => theme.spacing(4)}px;
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

interface ProgramDetailsProps {
  program: ProgramQuery['program'];
  choices: ProgrammeChoiceDataQuery;
}

export const ProgramDetails = ({
  program,
  choices,
}: ProgramDetailsProps): React.ReactElement => {
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
        <Typography variant='h6'>{t('Details')}</Typography>
      </Title>
      <OverviewContainer>
        <Grid container>
          <Grid container item xs={9} spacing={6}>
            <Grid item xs={4}>
              <LabelizedField label={t('status')}>
                <StatusBox
                  status={program.status}
                  statusToColor={programStatusToColor}
                />
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
              <LabelizedField label={t('Organization')} value={<Missing />} />
            </Grid>
            <Grid item xs={4}>
              <LabelizedField
                label={t('Sector')}
                value={programSectorChoicesDict[program.sector]}
              />
            </Grid>
            <Grid item xs={4}>
              <LabelizedField
                label={t('Description')}
                value={program.description}
              />
            </Grid>
            <Grid item xs={4}>
              <LabelizedField label={t('Budget')} value={<Missing />} />
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
                label={t('CASH+')}
                value={program.cashPlus ? t('Yes') : t('No')}
              />
            </Grid>
          </Grid>
          <Grid item xs={3}>
            <NumberOfHouseHolds>
              <LabelizedField label={t('Program Population Size')}>
                <NumberOfHouseHoldsValue>
                  {program.totalNumberOfHouseholds === 0
                    ? '-'
                    : program.totalNumberOfHouseholds}
                </NumberOfHouseHoldsValue>
              </LabelizedField>
            </NumberOfHouseHolds>
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
                label={t('Data Collecting Type')}
                value={program?.dataCollectingType?.label}
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
        </Grid>
      </OverviewContainer>
    </ContainerColumnWithBorder>
  );
};
