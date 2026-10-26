import { LabelizedField } from '@core/LabelizedField';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import { Box, Typography } from '@mui/material';
import { DisabilityEnum } from '@restgenerated/models/DisabilityEnum';
import type { IndividualDetail } from '@restgenerated/models/IndividualDetail';
import {
  choicesToDict,
  displayNameWithLatin,
  formatAge,
  getPhoneNoLabel,
  renderBoolean,
  sexToCapitalize,
} from '@utils/utils';
import type { ReactElement, ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import { ResponsiveGrid, ResponsiveGridContainer } from 'src/responsive';
import styled from 'styled-components';
import { useProgramContext } from '../../../programContext';
import { DocumentPopulationPhotoModal } from '../../population/DocumentPopulationPhotoModal';
import { LinkedGrievancesModal } from '../../population/LinkedGrievancesModal/LinkedGrievancesModal';
import { BlackLink } from '@components/core/BlackLink';
import { IndividualPhotoModal } from '@components/population/IndividualPhotoModal';
import { Overview } from '@components/payments/Overview';
import type { IndividualChoices } from '@restgenerated/models/IndividualChoices';
import type { GrievanceChoices } from '@restgenerated/models/GrievanceChoices';
import type { HouseholdDetail } from '@restgenerated/models/HouseholdDetail';
import { RelationshipEnum } from '@restgenerated/models/RelationshipEnum';

const BorderBox = styled.div`
  border-bottom: 1px solid #e1e1e1;
`;

interface PeopleBioDataProps {
  individual: IndividualDetail;
  baseUrl: string;
  businessArea: string;
  choicesData: IndividualChoices;
  grievancesChoices: GrievanceChoices;
  household?: HouseholdDetail;
}
export const PeopleBioData = ({
  individual,
  baseUrl,
  businessArea,
  choicesData,
  grievancesChoices,
  household,
}: PeopleBioDataProps): ReactElement => {
  const { t } = useTranslation();
  const { selectedProgram } = useProgramContext();
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
          <LabelizedField label={doc.type?.label}>
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
        <LabelizedField label="issued">{doc.country?.name}</LabelizedField>
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

  const renderDelegate = (): ReactNode | null => {
    const alternateRole = (household?.rolesInHousehold as any[])?.find(
      (r) => r.role === 'ALTERNATE',
    );
    const delegate = alternateRole?.individual;

    return (
      <>
        <ResponsiveGrid size="full">
          <BorderBox />
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Delegate')}>
            {delegate?.unicefId ? (
              <BlackLink to={`/${baseUrl}/population/people/${delegate.id}`}>
                {delegate.unicefId}
              </BlackLink>
            ) : (
              '-'
            )}
          </LabelizedField>
        </ResponsiveGrid>
      </>
    );
  };

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

  let peopleFromHouseholdData = null;
  if (individual?.household) {
    const household = individual.household;
    peopleFromHouseholdData = (
      <>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Residence Status')}>
            {household?.residenceStatus}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Type')}>
            {individual.relationship === RelationshipEnum.HEAD
              ? t('Beneficiary')
              : t('Non-beneficiary')}{' '}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Country')}>
            {household?.country}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Country of Origin')}>
            {household.countryOrigin}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Address')}>
            {household.address}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Vilage')}>
            {household.village}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Zip Code')}>
            {household.zipCode}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Administrative Level 1')}>
            {household?.admin1?.name}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Administrative Level 2')}>
            {household?.admin2?.name}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Administrative Level 3')}>
            {household?.admin3?.name}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Administrative Level 4')}>
            {household?.admin4?.name}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="half">
          <LabelizedField label={t('Geolocation')}>
            {household?.geopoint}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Data Collecting Type')}>
            {selectedProgram?.dataCollectingType?.label}
          </LabelizedField>
        </ResponsiveGrid>
      </>
    );
  }

  return (
    <Overview>
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
          <LabelizedField label={t('Role')}>
            {roleChoicesDict[individual?.role ?? '']}
          </LabelizedField>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Preferred language')}>
            {individual?.preferredLanguage}
          </LabelizedField>
        </ResponsiveGrid>
        {peopleFromHouseholdData}
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
        {renderDelegate()}
      </ResponsiveGridContainer>
    </Overview>
  );
};
