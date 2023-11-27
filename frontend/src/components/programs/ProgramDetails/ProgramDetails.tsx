import { Box, Grid, Typography } from '@material-ui/core';
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
import { OverviewContainer } from '../../core/OverviewContainer';
import { StatusBox } from '../../core/StatusBox';
import { Title } from '../../core/Title';
import { UniversalMoment } from '../../core/UniversalMoment';
import { BaseSection } from '../../core/BaseSection';

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

const StyledBox = styled(Box)`
  border: 1px solid #e3e3e3;
`;

interface ProgramDetailsProps {
  program: ProgramQuery['program'];
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

  //TODO: remove this
  const partners = [
    {
      id: '9bef9d07-d45b-4291-ade6-3227311f3cea',
      partner: 'Partner ABC',
      areaAccess: 'ADMIN_AREA',
      adminAreas: [
        '6d49768f-e5fc-4f33-92f0-5004c31dcaf5',
        '705f5c09-484a-41d7-9aa4-6c7418d4ec80',
        '1841435e-d530-4f87-8aa6-7b1828f4c4a3',
        'e3c08a14-c47d-4b7a-b9e4-893dccac9622',
      ],
    },
    {
      partner: 'Partner XYZ',
      id: '423a9e1c-4e21-485e-801d-808091e9808f',
      areaAccess: 'BUSINESS_AREA',
    },
    {
      partner: 'Partner 123',
      id: 'ef356928-fbdf-442d-90e9-d444a2488e77',
      areaAccess: 'ADMIN_AREA',
      adminAreas: [
        '6d49768f-e5fc-4f33-92f0-5004c31dcaf5',
        '705f5c09-484a-41d7-9aa4-6c7418d4ec80',
      ],
    },
  ];
  return (
    <ContainerColumnWithBorder data-cy='program-details-container'>
      <Title>
        <Typography variant='h6'>{t('Programme Details')}</Typography>
      </Title>
      <OverviewContainer>
        <Grid container spacing={6}>
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
        <NumberOfHouseHolds>
          <LabelizedField label={t('Total Number of Households')}>
            <NumberOfHouseHoldsValue>
              {program.totalNumberOfHouseholds}
            </NumberOfHouseHoldsValue>
          </LabelizedField>
        </NumberOfHouseHolds>
      </OverviewContainer>
      <BaseSection p={0} noPaper title={t('Programme Partners')}>
        <Box mt={2}>
          <Grid container spacing={6}>
            {partners.map((partner) => (
              <Grid item xs={3}>
                <StyledBox p={6} flexDirection='column'>
                  <Typography variant='h6'>{partner.partner}</Typography>
                  <LabelizedField
                    label={t('Area Access')}
                    value={
                      partner.areaAccess === 'BUSINESS_AREA'
                        ? t('Business Area')
                        : `Admin Areas: ${partner.adminAreas?.length || 0}`
                    }
                  />
                </StyledBox>
              </Grid>
            ))}
          </Grid>
        </Box>
      </BaseSection>
    </ContainerColumnWithBorder>
  );
}
