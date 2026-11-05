import { ContentLink } from '@components/core/ContentLink';
import { LabelizedField } from '@core/LabelizedField';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { Box, Paper, Typography } from '@mui/material';
import type { IndividualChoices } from '@restgenerated/models/IndividualChoices';
import type { IndividualDetail } from '@restgenerated/models/IndividualDetail';
import {
  choicesToDict,
  displayNameWithLatin,
  formatAge,
  getPhoneNoLabel,
  renderBoolean,
  sexToCapitalize,
} from '@utils/utils';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useProgramContext } from 'src/programContext';
import {
  ResponsiveGrid,
  ResponsiveGridContainer,
  SECTION_PADDING,
} from 'src/responsive';
import styled from 'styled-components';
import { DocumentRegistrationPhotoModal } from '../DocumentRegistrationPhotoModal';

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
    <ResponsiveGrid key={doc.id} size="quarter">
      <Box
        sx={{
          flexDirection: 'column',
        }}
      >
        <Box
          sx={{
            mb: 1,
          }}
        >
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
    </ResponsiveGrid>
  ));

  const mappedIdentities = individual.identities?.map((item) => (
    <ResponsiveGrid key={item.id} size="quarter">
      <Box
        sx={{
          flexDirection: 'column',
        }}
      >
        <Box
          sx={{
            mb: 1,
          }}
        >
          <LabelizedField label={`${item.partner} ID`}>
            {item.number}
          </LabelizedField>
        </Box>
        <LabelizedField label={t('issued')}>{item.country.name}</LabelizedField>
      </Box>
    </ResponsiveGrid>
  ));

  return (
    <Paper sx={{ padding: SECTION_PADDING }}>
      <Title>
        <Typography variant="h6">{t('Bio Data')}</Typography>
      </Title>
      <ResponsiveGridContainer spacing={6}>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Full Name')}>
            {displayNameWithLatin(individual, 'fullName')}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Given Name')}>
            {displayNameWithLatin(individual, 'givenName')}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Middle Name')}>
            {displayNameWithLatin(individual, 'middleName')}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Family Name')}>
            {displayNameWithLatin(individual, 'familyName')}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Gender')}>
            {sexToCapitalize(individual.sex)}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Age')}>
            {formatAge(individual.age)}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Date of Birth')}>
            <UniversalMoment>{individual.birthDate}</UniversalMoment>
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Estimated Date of Birth')}>
            {renderBoolean(individual.estimatedBirthDate)}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Marital Status')}>
            {maritalStatusChoicesDict[individual.maritalStatus ?? '']}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Work Status')}>
            {workStatusChoicesDict[individual.workStatus ?? '']}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Pregnant')}>
            {renderBoolean(individual.pregnant)}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
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
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Role')}>
            {roleChoicesDict[individual.role ?? '']}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Relationship to HOH')}>
            {relationshipChoicesDict[individual.relationship ?? '']}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Preferred language')}>
            {individual.preferredLanguage}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="full">
          <BorderBox />
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Observed disabilities')}>
            {
              observedDisabilityChoicesDict[
                individual?.observedDisability ?? ''
              ]
            }
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Seeing disability severity')}>
            {severityOfDisabilityChoicesDict[individual.seeingDisability ?? '']}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Hearing disability severity')}>
            {
              severityOfDisabilityChoicesDict[
                individual.hearingDisability ?? ''
              ]
            }
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Physical disability severity')}>
            {
              severityOfDisabilityChoicesDict[
                individual.physicalDisability ?? ''
              ]
            }
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField
            label={t('Remembering or concentrating disability severity')}
          >
            {severityOfDisabilityChoicesDict[individual.memoryDisability ?? '']}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Self-care disability severity')}>
            {
              severityOfDisabilityChoicesDict[
                individual.selfcareDisability ?? ''
              ]
            }
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Communicating disability severity')}>
            {severityOfDisabilityChoicesDict[individual.commsDisability ?? '']}
          </LabelizedField>
        </ResponsiveGrid>
        {/* <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Disability')}>
            {individual.disability === 'DISABLED' ? 'Disabled' : 'Not Disabled'}
          </LabelizedField>
        </ResponsiveGrid> */}
        {!mappedIndividualDocuments?.length &&
        !mappedIdentities.length ? null : (
          <ResponsiveGrid size="full">
            <BorderBox />
          </ResponsiveGrid>
        )}
        {mappedIndividualDocuments}
        {mappedIdentities}
        <ResponsiveGrid size="full">
          <BorderBox />
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Email')}>
            {individual?.email}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Phone Number')}>
            {getPhoneNoLabel(individual.phoneNo, individual.phoneNoValid)}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Alternate Phone Number')}>
            {getPhoneNoLabel(
              individual.phoneNoAlternative,
              individual.phoneNoAlternativeValid,
            )}
          </LabelizedField>
        </ResponsiveGrid>
      </ResponsiveGridContainer>
    </Paper>
  );
}
