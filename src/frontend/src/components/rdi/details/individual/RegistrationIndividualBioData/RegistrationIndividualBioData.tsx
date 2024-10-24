import { Box, Grid, Paper, Typography } from '@mui/material';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import {
  choicesToDict,
  formatAge,
  getPhoneNoLabel,
  renderBoolean,
  sexToCapitalize,
} from '@utils/utils';
import {
  HouseholdChoiceDataQuery,
  ImportedIndividualDetailedFragment,
} from '@generated/graphql';
import { ContentLink } from '@core/ContentLink';
import { LabelizedField } from '@core/LabelizedField';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import { DocumentRegistrationPhotoModal } from '../DocumentRegistrationPhotoModal';
import { useBaseUrl } from '@hooks/useBaseUrl';

const Overview = styled(Paper)`
  padding: ${({ theme }) => theme.spacing(8)}
    ${({ theme }) => theme.spacing(11)};
`;

const BorderBox = styled.div`
  border-bottom: 1px solid #e1e1e1;
`;

interface RegistrationIndividualBioDataProps {
  individual: ImportedIndividualDetailedFragment;
  choicesData: HouseholdChoiceDataQuery;
}

export function RegistrationIndividualBioData({
  individual,
  choicesData,
}: RegistrationIndividualBioDataProps): React.ReactElement {
  const { baseUrl } = useBaseUrl();
  const { t } = useTranslation();
  const relationshipChoicesDict = choicesToDict(
    choicesData.relationshipChoices,
  );
  const maritalStatusChoicesDict = choicesToDict(
    choicesData.maritalStatusChoices,
  );
  const workStatusChoicesDict = choicesToDict(choicesData.workStatusChoices);
  const observedDisabilityChoicesDict = choicesToDict(
    choicesData.observedDisabilityChoices,
  );
  const severityOfDisabilityChoicesDict = choicesToDict(
    choicesData.severityOfDisabilityChoices,
  );
  const roleChoicesDict = choicesToDict(choicesData.roleChoices);
  const mappedIndividualDocuments = individual.documents?.edges?.map((edge) => (
    <Grid key={edge.node.id} item xs={3}>
      <Box flexDirection="column">
        <Box mb={1}>
          <LabelizedField label={edge.node.type.label}>
            {edge.node.photo ? (
              <DocumentRegistrationPhotoModal
                documentNumber={edge.node.documentNumber}
                documentId={edge.node.id}
                individual={individual}
              />
            ) : (
              edge.node.documentNumber
            )}
          </LabelizedField>
        </Box>
        <LabelizedField label={t('issued')}>{edge.node.country}</LabelizedField>
      </Box>
    </Grid>
  ));

  const mappedIdentities = individual.identities?.edges?.map((item) => (
    <Grid key={item.node.id} item xs={3}>
      <Box flexDirection="column">
        <Box mb={1}>
          <LabelizedField label={`${item.node.partner} ID`}>
            {item.node.number}
          </LabelizedField>
        </Box>
        <LabelizedField label={t('issued')}>{item.node.country}</LabelizedField>
      </Box>
    </Grid>
  ));

  return (
    <Overview>
      <Title>
        <Typography variant="h6">{t('Bio Data')}</Typography>
      </Title>
      <Grid container spacing={6}>
        <Grid item xs={3}>
          <LabelizedField label={t('Full Name')}>
            {individual.fullName}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Given Name')}>
            {individual.givenName}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Middle Name')}>
            {individual.middleName}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Family Name')}>
            {individual.familyName}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Gender')}>
            {sexToCapitalize(individual.sex)}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Age')}>
            {formatAge(individual.age)}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Date of Birth')}>
            <UniversalMoment>{individual.birthDate}</UniversalMoment>
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Estimated Date of Birth')}>
            {renderBoolean(individual.estimatedBirthDate)}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Marital Status')}>
            {maritalStatusChoicesDict[individual.maritalStatus]}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Work Status')}>
            {workStatusChoicesDict[individual.workStatus]}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Pregnant')}>
            {renderBoolean(individual.pregnant)}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Household ID')}>
            {individual?.household?.id ? (
              <ContentLink
                href={`/${baseUrl}/registration-data-import/household/${individual?.household?.id}`}
              >
                {individual?.household.importId}
              </ContentLink>
            ) : (
              '-'
            )}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Role')}>
            {roleChoicesDict[individual.role]}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Relationship to HOH')}>
            {relationshipChoicesDict[individual.relationship]}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Preferred language')}>
            {individual.preferredLanguage}
          </LabelizedField>
        </Grid>
        <Grid item xs={12}>
          <BorderBox />
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Observed disabilities')}>
            {individual.observedDisability
              .map((choice) => observedDisabilityChoicesDict[choice])
              .join(', ')}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Seeing disability severity')}>
            {severityOfDisabilityChoicesDict[individual.seeingDisability]}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Hearing disability severity')}>
            {severityOfDisabilityChoicesDict[individual.hearingDisability]}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Physical disability severity')}>
            {severityOfDisabilityChoicesDict[individual.physicalDisability]}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField
            label={t('Remembering or concentrating disability severity')}
          >
            {severityOfDisabilityChoicesDict[individual.memoryDisability]}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Self-care disability severity')}>
            {severityOfDisabilityChoicesDict[individual.selfcareDisability]}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Communicating disability severity')}>
            {severityOfDisabilityChoicesDict[individual.commsDisability]}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Disability')}>
            {individual.disability === 'DISABLED' ? 'Disabled' : 'Not Disabled'}
          </LabelizedField>
        </Grid>
        {!mappedIndividualDocuments?.length &&
        !mappedIdentities.length ? null : (
          <Grid item xs={12}>
            <BorderBox />
          </Grid>
        )}
        {mappedIndividualDocuments}
        {mappedIdentities}
        <Grid item xs={12}>
          <BorderBox />
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Email')}>
            {individual?.email}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Phone Number')}>
            {getPhoneNoLabel(individual.phoneNo, individual.phoneNoValid)}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Alternate Phone Number')}>
            {getPhoneNoLabel(
              individual.phoneNoAlternative,
              individual.phoneNoAlternativeValid,
            )}
          </LabelizedField>
        </Grid>
      </Grid>
    </Overview>
  );
}
