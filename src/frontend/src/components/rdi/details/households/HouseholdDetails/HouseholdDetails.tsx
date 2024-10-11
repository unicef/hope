import { Grid, Typography } from '@mui/material';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { ContentLink } from '@core/ContentLink';
import { LabelizedField } from '@core/LabelizedField';
import { choicesToDict } from '@utils/utils';
import {
  HouseholdChoiceDataQuery,
  ImportedHouseholdDetailedFragment,
} from '@generated/graphql';
import { Title } from '@core/Title';
import { useProgramContext } from '../../../../../programContext';
import { useBaseUrl } from '@hooks/useBaseUrl';

const Overview = styled.div`
  display: flex;
  flex-direction: row;
  width: 100%;
`;

interface HouseholdDetailsProps {
  household: ImportedHouseholdDetailedFragment;
  choicesData: HouseholdChoiceDataQuery;
}
export function HouseholdDetails({
  household,
  choicesData,
}: HouseholdDetailsProps): React.ReactElement {
  const { baseUrl } = useBaseUrl();
  const { t } = useTranslation();
  const { selectedProgram } = useProgramContext();
  const residenceChoicesDict = choicesToDict(
    choicesData.residenceStatusChoices,
  );
  return (
    <ContainerColumnWithBorder>
      <Title>
        <Typography variant="h6">{t('Details')}</Typography>
      </Title>
      <Overview>
        <Grid container spacing={6}>
          <Grid item xs={3}>
            <LabelizedField label={t('Household Size')}>
              {household.size}
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label={t('Country')}>
              {household.country}
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label={t('Residence Status')}>
              {residenceChoicesDict[household.residenceStatus]}
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label={t('Country of Origin')}>
              {household.countryOrigin}
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label={t('Head of Household')}>
              <ContentLink
                href={`/${baseUrl}/registration-data-import/individual/${household.headOfHousehold.id}`}
              >
                {household.headOfHousehold.fullName}
              </ContentLink>
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label={t('FEMALE CHILD HEADED HOUSEHOLD')}>
              {household.fchildHoh ? 'Yes' : 'No'}
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label={t('CHILD HEADED HOUSEHOLD')}>
              {household.childHoh ? 'Yes' : 'No'}
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label={t('ADMINISTRATIVE LEVEL 1')}>
              {household.admin1?.name}
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label={t('ADMINISTRATIVE LEVEL 2')}>
              {household.admin2?.name}
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label={t('Data Collecting Type')}>
              {selectedProgram?.dataCollectingType?.label}
            </LabelizedField>
          </Grid>
        </Grid>
      </Overview>
    </ContainerColumnWithBorder>
  );
}
