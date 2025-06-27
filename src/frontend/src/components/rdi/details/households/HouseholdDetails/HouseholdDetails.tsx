import { Grid2 as Grid, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { ContentLink } from '@core/ContentLink';
import { LabelizedField } from '@core/LabelizedField';
import { choicesToDict } from '@utils/utils';
import {
  HouseholdChoiceDataQuery,
  HouseholdDetailedFragment,
} from '@generated/graphql';
import { Title } from '@core/Title';
import { useProgramContext } from '../../../../../programContext';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ReactElement } from 'react';

const Overview = styled.div`
  display: flex;
  flex-direction: row;
  width: 100%;
`;

interface HouseholdDetailsProps {
  household: HouseholdDetailedFragment;
  choicesData: HouseholdChoiceDataQuery;
}
export function HouseholdDetails({
  household,
  choicesData,
}: HouseholdDetailsProps): ReactElement {
  const { baseUrl } = useBaseUrl();
  const { t } = useTranslation();
  const { selectedProgram } = useProgramContext();
  const residenceChoicesDict = choicesToDict(
    choicesData.residenceStatusChoices,
  );
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  return (
    <ContainerColumnWithBorder>
      <Title>
        <Typography variant="h6">{t('Details')}</Typography>
      </Title>
      <Overview>
        <Grid container spacing={6}>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={`${beneficiaryGroup?.groupLabel} Size`}>
              {household.size}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Country')}>
              {household.country}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Residence Status')}>
              {residenceChoicesDict[household.residenceStatus]}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Country of Origin')}>
              {household.countryOrigin}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={`Head of ${beneficiaryGroup?.groupLabel}`}>
              <ContentLink
                href={`/${baseUrl}/registration-data-import/individual/${household.headOfHousehold.id}`}
              >
                {household.headOfHousehold.fullName}
              </ContentLink>
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('FEMALE CHILD HEADED HOUSEHOLD')}>
              {household.fchildHoh ? 'Yes' : 'No'}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('CHILD HEADED HOUSEHOLD')}>
              {household.childHoh ? 'Yes' : 'No'}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('ADMINISTRATIVE LEVEL 1')}>
              {household.admin1?.name}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('ADMINISTRATIVE LEVEL 2')}>
              {household.admin2?.name}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Data Collecting Type')}>
              {selectedProgram?.dataCollectingType?.label}
            </LabelizedField>
          </Grid>
        </Grid>
      </Overview>
    </ContainerColumnWithBorder>
  );
}
