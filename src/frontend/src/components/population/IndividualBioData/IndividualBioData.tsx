import { Box, Paper, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import {
  ResponsiveGrid,
  ResponsiveGridContainer,
  SECTION_PADDING,
} from 'src/responsive';
import styled from 'styled-components';
import {
  choicesToDict,
  displayNameWithLatin,
  formatAge,
  getPhoneNoLabel,
  renderBoolean,
  sexToCapitalize,
} from '@utils/utils';
import { BlackLink } from '@core/BlackLink';
import { ContentLink } from '@core/ContentLink';
import { LabelizedField } from '@core/LabelizedField';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import { DocumentPopulationPhotoModal } from '../DocumentPopulationPhotoModal';
import { LinkedGrievancesModal } from '../LinkedGrievancesModal/LinkedGrievancesModal';
import { useProgramContext } from 'src/programContext';
import type { ReactElement, ReactNode } from 'react';
import type { IndividualDetail } from '@restgenerated/models/IndividualDetail';
import { DisabilityEnum } from '@restgenerated/models/DisabilityEnum';
import type { IndividualChoices } from '@restgenerated/models/IndividualChoices';
import type { GrievanceChoices } from '@restgenerated/models/GrievanceChoices';
import { IndividualPhotoModal } from '@components/population/IndividualPhotoModal';

const BorderBox = styled.div`
  border-bottom: 1px solid #e1e1e1;
`;

interface IndividualBioDataProps {
  individual: IndividualDetail;
  baseUrl: string;
  businessArea: string;
  choicesData: IndividualChoices;
  grievancesChoices: GrievanceChoices;
}
export const IndividualBioData = ({
  individual,
  baseUrl,
  businessArea,
  choicesData,
  grievancesChoices,
}: IndividualBioDataProps): ReactElement => {
  const { t } = useTranslation();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const relationshipChoicesDict = choicesToDict(
    choicesData.relationshipChoices,
  );
  const maritalStatusChoicesDict = choicesToDict(
    choicesData.maritalStatusChoices,
  );
  const workStatusChoicesDict = choicesToDict(choicesData.workStatusChoices);
  const roleChoicesDict = choicesToDict(choicesData.roleChoices);

  const severityOfDisabilityChoicesDict = choicesToDict(
    choicesData.severityOfDisabilityChoices,
  );

  const observedDisabilityChoicesDict = choicesToDict(
    choicesData.observedDisabilityChoices,
  );

  const mappedIndividualDocuments = individual?.documents?.map((doc) => (
    <ResponsiveGrid size="quarter" key={doc.id}>
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
              <DocumentPopulationPhotoModal
                documentNumber={doc.documentNumber}
                documentId={doc.id}
                individual={individual}
              />
            ) : (
              doc.documentNumber
            )}
          </LabelizedField>
        </Box>
        <LabelizedField label="issued">{doc.country.name}</LabelizedField>
      </Box>
    </ResponsiveGrid>
  ));

  const mappedIdentities = individual?.identities?.map((item) => (
    <ResponsiveGrid size="quarter" key={item.id}>
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
        <LabelizedField label="issued">{item.country.name}</LabelizedField>
      </Box>
    </ResponsiveGrid>
  ));

  const mappedRoles = (
    <ResponsiveGrid size="quarter" mobileSize="half">
      <LabelizedField label={`Linked ${beneficiaryGroup?.groupLabelPlural}`}>
        {individual?.rolesInHouseholds?.length
          ? individual?.rolesInHouseholds?.map((item) => (
              <Box key={item.id}>
                {item.household.unicefId} -{roleChoicesDict[item.role]}
              </Box>
            ))
          : '-'}
      </LabelizedField>
    </ResponsiveGrid>
  );

  const renderBiometricDataSection = (): ReactNode => {
    if (!individual.biometricDeduplicationGoldenRecordStatus) {
      return null;
    }

    const biometricCheckRun =
      individual.biometricDeduplicationGoldenRecordStatus !== 'Not Processed';
    const biometricTickets: Array<{
      id: string;
      unicefId: string;
      category: number;
    }> = (individual.linkedGrievancesBiometrics as any) ?? [];

    return (
      <>
        <ResponsiveGrid size="full">
          <BorderBox />
        </ResponsiveGrid>
        <ResponsiveGrid size="full">
          <Typography variant="h6">{t('Biometric Data')}</Typography>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Biometric Trait')}>
            {individual.photo ? (
              <IndividualPhotoModal individual={individual} />
            ) : null}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Biometric Check')}>
            {biometricCheckRun ? t('Was run') : t('Was not run')}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Tickets related')}>
            {biometricTickets.length > 0
              ? biometricTickets.map((ticket) => {
                  return (
                    <Box key={ticket.id}>
                      <BlackLink
                        to={`/${baseUrl}/grievance/tickets/
                          system-generated/${ticket.id}`}
                      >
                        {ticket.unicefId}
                      </BlackLink>
                    </Box>
                  );
                })
              : null}
          </LabelizedField>
        </ResponsiveGrid>
      </>
    );
  };

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
            {sexToCapitalize(individual?.sex)}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Age')}>
            {formatAge(individual?.age)}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Date of Birth')}>
            <UniversalMoment>{individual?.birthDate}</UniversalMoment>
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Estimated Date of Birth')}>
            {renderBoolean(individual?.estimatedBirthDate)}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Marital Status')}>
            {maritalStatusChoicesDict[individual?.maritalStatus ?? '']}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Work Status')}>
            {workStatusChoicesDict[individual?.workStatus ?? '']}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Pregnant')}>
            {renderBoolean(individual?.pregnant)}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={`${beneficiaryGroup?.groupLabel} ID`}>
            {individual?.household?.id ? (
              <ContentLink
                href={`/${baseUrl}/population/household/${individual?.household?.id}`}
              >
                {individual?.household?.unicefId}
              </ContentLink>
            ) : (
              <span>-</span>
            )}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Role')}>
            {roleChoicesDict[individual?.role ?? '']}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField
            label={`Relationship to Head Of ${beneficiaryGroup?.groupLabel}`}
          >
            {relationshipChoicesDict[individual?.relationship ?? '']}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Preferred language')}>
            {individual?.preferredLanguage}
          </LabelizedField>
        </ResponsiveGrid>
        {mappedRoles}
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
            {
              severityOfDisabilityChoicesDict[
                individual?.seeingDisability ?? ''
              ]
            }
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Hearing disability severity')}>
            {
              severityOfDisabilityChoicesDict[
                individual?.hearingDisability ?? ''
              ]
            }
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Physical disability severity')}>
            {
              severityOfDisabilityChoicesDict[
                individual?.physicalDisability ?? ''
              ]
            }
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField
            label={t('Remembering or concentrating disability severity')}
          >
            {
              severityOfDisabilityChoicesDict[
                individual?.memoryDisability ?? ''
              ]
            }
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Self-care disability severity')}>
            {
              severityOfDisabilityChoicesDict[
                individual?.selfcareDisability ?? ''
              ]
            }
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Communicating disability severity')}>
            {severityOfDisabilityChoicesDict[individual?.commsDisability ?? '']}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Disability')}>
            {individual?.disability === DisabilityEnum.DISABLED
              ? 'Disabled'
              : 'Not Disabled'}
          </LabelizedField>
        </ResponsiveGrid>
        {!mappedIndividualDocuments?.length &&
        !mappedIdentities?.length ? null : (
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
            {getPhoneNoLabel(individual?.phoneNo, individual?.phoneNoValid)}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Alternative Phone Number')}>
            {getPhoneNoLabel(
              individual?.phoneNoAlternative,
              individual?.phoneNoAlternativeValid,
            )}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField
            label={individual.identificationKeyLabel || t('Identification Key')}
          >
            {individual?.identificationKey}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="full">
          <BorderBox />
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField
            label={t('Date of last screening against sanctions list')}
          >
            <UniversalMoment>
              {individual?.sanctionListLastCheck}
            </UniversalMoment>
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="half">
          {individual?.household?.unicefId && (
            <LinkedGrievancesModal
              household={individual?.household}
              baseUrl={baseUrl}
              businessArea={businessArea}
              grievancesChoices={grievancesChoices}
            />
          )}
        </ResponsiveGrid>
        {renderBiometricDataSection()}
      </ResponsiveGridContainer>
    </Paper>
  );
};
