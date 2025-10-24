import { ContentLink } from '@components/core/ContentLink';
import { LabelizedField } from '@core/LabelizedField';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { Box, Grid, Paper, Theme, Typography } from '@mui/material';
import { IndividualChoices } from '@restgenerated/models/IndividualChoices';
import { IndividualDetail } from '@restgenerated/models/IndividualDetail';
import {
  choicesToDict,
  formatAge,
  getPhoneNoLabel,
  renderBoolean,
  sexToCapitalize,
} from '@utils/utils';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useProgramContext } from 'src/programContext';
import styled from 'styled-components';
import { DocumentRegistrationPhotoModal } from '../DocumentRegistrationPhotoModal';

const Overview = styled(Paper)<{ theme?: Theme }>`
  padding: ${({ theme }) => theme.spacing(8)}
    ${({ theme }) => theme.spacing(11)};
`;

const BorderBox = styled.div`
  border-bottom: 1px solid #e1e1e1;
`;

interface RegistrationIndividualBioDataProps {
  individual: IndividualDetail;
  choicesData: IndividualChoices;
}

export function RegistrationIndividualBioData({
  individual,
  choicesData,
}: RegistrationIndividualBioDataProps): ReactElement {
  const { t } = useTranslation();
  const { selectedProgram } = useProgramContext();
  const { baseUrl } = useBaseUrl();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const relationshipChoicesDict = choicesToDict(
    choicesData.relationshipChoices,
  );
  const maritalStatusChoicesDict = choicesToDict(
    choicesData.maritalStatusChoices,
  );
  const workStatusChoicesDict = choicesToDict(choicesData.workStatusChoices);

  const severityOfDisabilityChoicesDict = choicesToDict(
    choicesData.severityOfDisabilityChoices,
  );

  const observedDisabilityChoicesDict = choicesToDict(
    choicesData.observedDisabilityChoices,
  );

  const roleChoicesDict = choicesToDict(choicesData.roleChoices);
  const mappedIndividualDocuments = individual.documents?.map((doc) => (
    <Grid key={doc.id} size={3}>
      <Box flexDirection="column">
        <Box mb={1}>
          <LabelizedField label={doc.type.label}>
            {doc.photo ? (
              <DocumentRegistrationPhotoModal
                documentNumber={doc.documentNumber}
                documentId={doc.id}
                individual={individual}
              />
            ) : (
              doc.documentNumber
            )}
          </LabelizedField>
        </Box>
        <LabelizedField label={t('issued')}>{doc.country.name}</LabelizedField>
      </Box>
    </Grid>
  ));

  const mappedIdentities = individual.identities?.map((item) => (
    <Grid key={item.id} size={3}>
      <Box flexDirection="column">
        <Box mb={1}>
          <LabelizedField label={`${item.partner} ID`}>
            {item.number}
          </LabelizedField>
        </Box>
        <LabelizedField label={t('issued')}>{item.country.name}</LabelizedField>
      </Box>
    </Grid>
  ));

  return (
    <Overview>
      <Title>
        <Typography variant="h6">{t('Bio Data')}</Typography>
      </Title>
      <Grid container spacing={6}>
        <Grid size={3}>
          <LabelizedField label={t('Full Name')}>
            {individual.fullName}
          </LabelizedField>
        </Grid>
        <Grid size={3}>
          <LabelizedField label={t('Given Name')}>
            {individual.givenName}
          </LabelizedField>
        </Grid>
        <Grid size={3}>
          <LabelizedField label={t('Middle Name')}>
            {individual.middleName}
          </LabelizedField>
        </Grid>
        <Grid size={3}>
          <LabelizedField label={t('Family Name')}>
            {individual.familyName}
          </LabelizedField>
        </Grid>
        <Grid size={3}>
          <LabelizedField label={t('Gender')}>
            {sexToCapitalize(individual.sex)}
          </LabelizedField>
        </Grid>
        <Grid size={3}>
          <LabelizedField label={t('Age')}>
            {formatAge(individual.age)}
          </LabelizedField>
        </Grid>
        <Grid size={3}>
          <LabelizedField label={t('Date of Birth')}>
            <UniversalMoment>{individual.birthDate}</UniversalMoment>
          </LabelizedField>
        </Grid>
        <Grid size={3}>
          <LabelizedField label={t('Estimated Date of Birth')}>
            {renderBoolean(individual.estimatedBirthDate)}
          </LabelizedField>
        </Grid>
        <Grid size={3}>
          <LabelizedField label={t('Marital Status')}>
            {maritalStatusChoicesDict[individual.maritalStatus]}
          </LabelizedField>
        </Grid>
        <Grid size={3}>
          <LabelizedField label={t('Work Status')}>
            {workStatusChoicesDict[individual.workStatus]}
          </LabelizedField>
        </Grid>
        <Grid size={3}>
          <LabelizedField label={t('Pregnant')}>
            {renderBoolean(individual.pregnant)}
          </LabelizedField>
        </Grid>
        <Grid size={3}>
          <LabelizedField label={t(`${beneficiaryGroup?.groupLabel} ID`)}>
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
        <Grid size={3}>
          <LabelizedField label={t('Role')}>
            {roleChoicesDict[individual.role]}
          </LabelizedField>
        </Grid>
        <Grid size={3}>
          <LabelizedField label={t('Relationship to HOH')}>
            {relationshipChoicesDict[individual.relationship]}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Preferred language')}>
            {individual.preferredLanguage}
          </LabelizedField>
        </Grid>
        <Grid size={12}>
          <BorderBox />
        </Grid>
        <Grid size={3}>
          <LabelizedField label={t('Observed disabilities')}>
            {observedDisabilityChoicesDict[individual?.observedDisability]}
          </LabelizedField>
        </Grid>
        <Grid size={3}>
          <LabelizedField label={t('Seeing disability severity')}>
            {severityOfDisabilityChoicesDict[individual.seeingDisability]}
          </LabelizedField>
        </Grid>
        <Grid size={3}>
          <LabelizedField label={t('Hearing disability severity')}>
            {severityOfDisabilityChoicesDict[individual.hearingDisability]}
          </LabelizedField>
        </Grid>
        <Grid size={3}>
          <LabelizedField label={t('Physical disability severity')}>
            {severityOfDisabilityChoicesDict[individual.physicalDisability]}
          </LabelizedField>
        </Grid>
        <Grid size={3}>
          <LabelizedField
            label={t('Remembering or concentrating disability severity')}
          >
            {severityOfDisabilityChoicesDict[individual.memoryDisability]}
          </LabelizedField>
        </Grid>
        <Grid size={3}>
          <LabelizedField label={t('Self-care disability severity')}>
            {severityOfDisabilityChoicesDict[individual.selfcareDisability]}
          </LabelizedField>
        </Grid>
        <Grid size={3}>
          <LabelizedField label={t('Communicating disability severity')}>
            {severityOfDisabilityChoicesDict[individual.commsDisability]}
          </LabelizedField>
        </Grid>
        {/* <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Disability')}>
            {individual.disability === 'DISABLED' ? 'Disabled' : 'Not Disabled'}
          </LabelizedField>
        </Grid> */}
        {!mappedIndividualDocuments?.length &&
        !mappedIdentities.length ? null : (
          <Grid size={{ xs: 12 }}>
            <BorderBox />
          </Grid>
        )}
        {mappedIndividualDocuments}
        {mappedIdentities}
        <Grid size={12}>
          <BorderBox />
        </Grid>
        <Grid size={3}>
          <LabelizedField label={t('Email')}>
            {individual?.email}
          </LabelizedField>
        </Grid>
        <Grid size={3}>
          <LabelizedField label={t('Phone Number')}>
            {getPhoneNoLabel(individual.phoneNo, individual.phoneNoValid)}
          </LabelizedField>
        </Grid>
        <Grid size={3}>
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
