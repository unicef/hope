import { LabelizedField } from '@core/LabelizedField';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import { Box, Grid2 as Grid, Typography } from '@mui/material';
import { DisabilityEnum } from '@restgenerated/models/DisabilityEnum';
import { IndividualDetail } from '@restgenerated/models/IndividualDetail';
import {
  choicesToDict,
  formatAge,
  getPhoneNoLabel,
  renderBoolean,
  sexToCapitalize,
} from '@utils/utils';
import { ReactElement, ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useProgramContext } from '../../../programContext';
import { DocumentPopulationPhotoModal } from '../../population/DocumentPopulationPhotoModal';
import { LinkedGrievancesModal } from '../../population/LinkedGrievancesModal/LinkedGrievancesModal';
import { Overview } from '@components/payments/Overview';
import { IndividualChoices } from '@restgenerated/models/IndividualChoices';
import { GrievanceChoices } from '@restgenerated/models/GrievanceChoices';

const BorderBox = styled.div`
  border-bottom: 1px solid #e1e1e1;
`;

interface PeopleBioDataProps {
  individual: IndividualDetail;
  baseUrl: string;
  businessArea: string;
  choicesData: IndividualChoices;
  grievancesChoices: GrievanceChoices;
}
export const PeopleBioData = ({
  individual,
  baseUrl,
  businessArea,
  choicesData,
  grievancesChoices,
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
    <Grid size={{ xs: 3 }} key={doc.id}>
      <Box flexDirection="column">
        <Box mb={1}>
          <LabelizedField label={doc.type}>
            {doc.image ? (
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
        <LabelizedField label="issued">{doc.country}</LabelizedField>
      </Box>
    </Grid>
  ));

  const mappedIdentities = individual?.identities?.map((item) => (
    <Grid size={{ xs: 3 }} key={item.id}>
      <Box flexDirection="column">
        <Box mb={1}>
          <LabelizedField label={`${item.partner} ID`}>
            {item.number}
          </LabelizedField>
        </Box>
        <LabelizedField label="issued">{item.country.name}</LabelizedField>
      </Box>
    </Grid>
  ));

  const renderDigitalWalletInfo = (): ReactNode => {
    return (
      <>
        <Grid size={{ xs: 12 }}>
          <BorderBox />
        </Grid>
        <Grid size={{ xs: 4 }}>
          <LabelizedField label={t('Wallet Name')}>
            {individual?.walletName}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 4 }}>
          <LabelizedField label={t('Blockchain Name')}>
            {individual?.blockchainName}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 4 }}>
          <LabelizedField label={t('Wallet Address')}>
            {individual?.walletAddress}
          </LabelizedField>
        </Grid>
      </>
    );
  };

  let peopleFromHouseholdData = null;
  if (individual?.household) {
    const household = individual.household;
    peopleFromHouseholdData = (
      <>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Residence Status')}>
            {household?.residenceStatus}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Country')}>
            {household?.country}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Country of Origin')}>
            {household.countryOrigin}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Address')}>
            {household.address}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Vilage')}>
            {household.village}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Zip Code')}>
            {household.zipCode}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Administrative Level 1')}>
            {household?.admin1?.name}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Administrative Level 2')}>
            {household?.admin2?.name}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Administrative Level 3')}>
            {household?.admin3?.name}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Administrative Level 4')}>
            {household?.admin4?.name}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 6 }}>
          <LabelizedField label={t('Geolocation')}>
            {household?.geopoint}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Data Collecting Type')}>
            {selectedProgram?.dataCollectingType?.label}
          </LabelizedField>
        </Grid>
      </>
    );
  }

  return (
    <Overview>
      <Title>
        <Typography variant="h6">{t('Bio Data')}</Typography>
      </Title>
      <Grid container spacing={6}>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Full Name')}>
            {individual?.fullName}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Given Name')}>
            {individual?.givenName}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Middle Name')}>
            {individual?.middleName}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Family Name')}>
            {individual?.familyName}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Gender')}>
            {sexToCapitalize(individual?.sex)}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Age')}>
            {formatAge(individual?.age)}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Date of Birth')}>
            <UniversalMoment>{individual?.birthDate}</UniversalMoment>
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Estimated Date of Birth')}>
            {renderBoolean(individual?.estimatedBirthDate)}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Marital Status')}>
            {maritalStatusChoicesDict[individual?.maritalStatus]}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Work Status')}>
            {workStatusChoicesDict[individual?.workStatus]}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Pregnant')}>
            {renderBoolean(individual?.pregnant)}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Role')}>
            {roleChoicesDict[individual?.role]}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Preferred language')}>
            {individual?.preferredLanguage}
          </LabelizedField>
        </Grid>
        {peopleFromHouseholdData}
        <Grid size={{ xs: 12 }}>
          <BorderBox />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Observed disabilities')}>
            {observedDisabilityChoicesDict[individual?.observedDisability]}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Seeing disability severity')}>
            {severityOfDisabilityChoicesDict[individual?.seeingDisability]}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Hearing disability severity')}>
            {severityOfDisabilityChoicesDict[individual?.hearingDisability]}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Physical disability severity')}>
            {severityOfDisabilityChoicesDict[individual?.physicalDisability]}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField
            label={t('Remembering or concentrating disability severity')}
          >
            {severityOfDisabilityChoicesDict[individual?.memoryDisability]}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Self-care disability severity')}>
            {severityOfDisabilityChoicesDict[individual?.selfcareDisability]}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Communicating disability severity')}>
            {severityOfDisabilityChoicesDict[individual?.commsDisability]}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Disability')}>
            {individual?.disability === DisabilityEnum.DISABLED
              ? 'Disabled'
              : 'Not Disabled'}
          </LabelizedField>
        </Grid>
        {!mappedIndividualDocuments?.length &&
        !mappedIdentities?.length ? null : (
          <Grid size={{ xs: 12 }}>
            <BorderBox />
          </Grid>
        )}
        {mappedIndividualDocuments}
        {mappedIdentities}
        <Grid size={{ xs: 12 }}>
          <BorderBox />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Email')}>
            {individual?.email}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Phone Number')}>
            {getPhoneNoLabel(individual?.phoneNo, individual?.phoneNoValid)}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Alternative Phone Number')}>
            {getPhoneNoLabel(
              individual?.phoneNoAlternative,
              individual?.phoneNoAlternativeValid,
            )}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 12 }}>
          <BorderBox />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField
            label={t('Date of last screening against sanctions list')}
          >
            <UniversalMoment>
              {individual?.sanctionListLastCheck}
            </UniversalMoment>
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 6 }}>
          {individual?.household?.unicefId && (
            <LinkedGrievancesModal
              household={individual?.household}
              baseUrl={baseUrl}
              businessArea={businessArea}
              grievancesChoices={grievancesChoices}
            />
          )}
        </Grid>
        {renderDigitalWalletInfo()}
      </Grid>
    </Overview>
  );
};
