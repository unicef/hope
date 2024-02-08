import { Box, Grid, Typography } from '@mui/material';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { ProgramQuery, ProgrammeChoiceDataQuery } from '@generated/graphql';
import { MiśTheme } from '../../../theme';
import { choicesToDict, programStatusToColor } from '@utils/utils';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { LabelizedField } from '@core/LabelizedField';
import { OverviewContainer } from '@core/OverviewContainer';
import { StatusBox } from '@core/StatusBox';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import { DividerLine } from '@core/DividerLine';

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
  const { programFrequencyOfPaymentsChoices, programSectorChoices } = choices;
  const programFrequencyOfPaymentsChoicesDict = choicesToDict(
    programFrequencyOfPaymentsChoices,
  );
  const programSectorChoicesDict = choicesToDict(programSectorChoices);

  return (
    <ContainerColumnWithBorder data-cy="program-details-container">
      <Title>
        <Typography variant="h6">{t('Programme Details')}</Typography>
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
        </Grid>
        <NumberOfHouseHolds>
          <LabelizedField label={t('Total Number of Households')}>
            <NumberOfHouseHoldsValue>
              {program.totalNumberOfHouseholds}
            </NumberOfHouseHoldsValue>
          </LabelizedField>
        </NumberOfHouseHolds>
      </OverviewContainer>
      {program.partners.length > 0 && (
        <>
          <DividerLine />
          <Title>
            <Typography variant="h6">{t('Programme Partners')}</Typography>
          </Title>
          <OverviewContainer>
            <Grid container spacing={6}>
              {program.partners.map((partner) => (
                <Grid key={partner.id} item xs={3}>
                  <StyledBox p={6} flexDirection="column">
                    <Typography data-cy="label-partner-name" variant="h6">
                      {partner.name}
                    </Typography>
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
          </OverviewContainer>
        </>
      )}
    </ContainerColumnWithBorder>
  );
}
