import { Grid, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { ContainerColumnWithBorder } from '../../../../components/ContainerColumnWithBorder';
import { ContentLink } from '../../../../components/ContentLink';
import { LabelizedField } from '../../../../components/LabelizedField';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { choicesToDict } from '../../../../utils/utils';
import {
  HouseholdChoiceDataQuery,
  ImportedHouseholdDetailedFragment,
} from '../../../../__generated__/graphql';

const Overview = styled.div`
  display: flex;
  flex-direction: row;
  width: 100%;
`;
const Title = styled.div`
  width: 100%;
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

interface HouseholdDetailsProps {
  household: ImportedHouseholdDetailedFragment;
  choicesData: HouseholdChoiceDataQuery;
}
export function HouseholdDetails({
  household,
  choicesData,
}: HouseholdDetailsProps): React.ReactElement {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();

  const residenceChoicesDict = choicesToDict(
    choicesData.residenceStatusChoices,
  );
  return (
    <ContainerColumnWithBorder>
      <Title>
        <Typography variant='h6'>{t('Details')}</Typography>
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
                href={`/${businessArea}/registration-data-import/individual/${household.headOfHousehold.id}`}
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
              {household.admin1Title}
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label={t('ADMINISTRATIVE LEVEL 2')}>
              {household.admin2Title}
            </LabelizedField>
          </Grid>
        </Grid>
      </Overview>
    </ContainerColumnWithBorder>
  );
}
