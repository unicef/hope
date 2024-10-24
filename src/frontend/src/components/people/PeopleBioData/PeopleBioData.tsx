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
  GrievancesChoiceDataQuery,
  HouseholdChoiceDataQuery,
  IndividualDisability,
  IndividualNode,
} from '@generated/graphql';
import { LabelizedField } from '@core/LabelizedField';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import { DocumentPopulationPhotoModal } from '../../population/DocumentPopulationPhotoModal';
import { LinkedGrievancesModal } from '../../population/LinkedGrievancesModal/LinkedGrievancesModal';
import { useProgramContext } from '../../../programContext';

const Overview = styled(Paper)`
  padding: ${({ theme }) => theme.spacing(8)}
    ${({ theme }) => theme.spacing(11)};
`;

const BorderBox = styled.div`
  border-bottom: 1px solid #e1e1e1;
`;

interface PeopleBioDataProps {
  individual: IndividualNode;
  baseUrl: string;
  businessArea: string;
  choicesData: HouseholdChoiceDataQuery;
  grievancesChoices: GrievancesChoiceDataQuery;
}
export const PeopleBioData = ({
  individual,
  baseUrl,
  businessArea,
  choicesData,
  grievancesChoices,
}: PeopleBioDataProps): React.ReactElement => {
  const { t } = useTranslation();
  const { selectedProgram } = useProgramContext();
  const maritalStatusChoicesDict = choicesToDict(
    choicesData.maritalStatusChoices,
  );
  const workStatusChoicesDict = choicesToDict(choicesData.workStatusChoices);
  const roleChoicesDict = choicesToDict(choicesData.roleChoices);
  const observedDisabilityChoicesDict = choicesToDict(
    choicesData.observedDisabilityChoices,
  );
  const severityOfDisabilityChoicesDict = choicesToDict(
    choicesData.severityOfDisabilityChoices,
  );

  const residenceChoicesDict = choicesToDict(
    choicesData.residenceStatusChoices,
  );

  const mappedIndividualDocuments = individual?.documents?.edges?.map(
    (edge) => (
      <Grid item xs={3} key={edge.node.id}>
        <Box flexDirection="column">
          <Box mb={1}>
            <LabelizedField label={edge.node.type.label}>
              {edge.node.photo ? (
                <DocumentPopulationPhotoModal
                  documentNumber={edge.node.documentNumber}
                  documentId={edge.node.id}
                  individual={individual}
                />
              ) : (
                edge.node.documentNumber
              )}
            </LabelizedField>
          </Box>
          <LabelizedField label="issued">{edge.node.country}</LabelizedField>
        </Box>
      </Grid>
    ),
  );

  const mappedIdentities = individual?.identities?.edges?.map((item) => (
    <Grid item xs={3} key={item.node.id}>
      <Box flexDirection="column">
        <Box mb={1}>
          <LabelizedField label={`${item.node.partner} ID`}>
            {item.node.number}
          </LabelizedField>
        </Box>
        <LabelizedField label="issued">{item.node.country}</LabelizedField>
      </Box>
    </Grid>
  ));

  const renderBankAccountInfo = (): React.ReactNode => {
    if (!individual?.bankAccountInfo) {
      return null;
    }
    return (
      <>
        <Grid item xs={12}>
          <BorderBox />
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Bank name')}>
            {individual?.bankAccountInfo?.bankName}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Bank account number')}>
            {individual?.bankAccountInfo?.bankAccountNumber}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Account holder name')}>
            {individual?.bankAccountInfo?.accountHolderName}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Bank branch name')}>
            {individual?.bankAccountInfo?.bankBranchName}
          </LabelizedField>
        </Grid>
      </>
    );
  };

  const renderDigitalWalletInfo = (): React.ReactNode => {
    return (
      <>
        <Grid item xs={12}>
          <BorderBox />
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label={t('Wallet Name')}>
            {individual?.walletName}
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label={t('Blockchain Name')}>
            {individual?.blockchainName}
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
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
        <Grid item xs={3}>
          <LabelizedField label={t('Residence Status')}>
            {residenceChoicesDict[household?.residenceStatus]}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Country')}>
            {household?.country}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Country of Origin')}>
            {household.countryOrigin}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Address')}>
            {household.address}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Vilage')}>
            {household.village}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Zip Code')}>
            {household.zipCode}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Administrative Level 1')}>
            {household?.admin1?.name}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Administrative Level 2')}>
            {household?.admin2?.name}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Administrative Level 3')}>
            {household?.admin3?.name}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Administrative Level 4')}>
            {household?.admin4?.name}
          </LabelizedField>
        </Grid>
        <Grid item xs={6}>
          <LabelizedField label={t('Geolocation')}>
            {household?.geopoint
              ? `${household?.geopoint?.coordinates[0]}, ${household?.geopoint?.coordinates[1]}`
              : '-'}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
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
        <Grid item xs={3}>
          <LabelizedField label={t('Full Name')}>
            {individual?.fullName}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Given Name')}>
            {individual?.givenName}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Middle Name')}>
            {individual?.middleName}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Family Name')}>
            {individual?.familyName}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Gender')}>
            {sexToCapitalize(individual?.sex)}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Age')}>
            {formatAge(individual?.age)}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Date of Birth')}>
            <UniversalMoment>{individual?.birthDate}</UniversalMoment>
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Estimated Date of Birth')}>
            {renderBoolean(individual?.estimatedBirthDate)}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Marital Status')}>
            {maritalStatusChoicesDict[individual?.maritalStatus]}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Work Status')}>
            {workStatusChoicesDict[individual?.workStatus]}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Pregnant')}>
            {renderBoolean(individual?.pregnant)}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Role')}>
            {roleChoicesDict[individual?.role]}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Preferred language')}>
            {individual?.preferredLanguage}
          </LabelizedField>
        </Grid>
        {peopleFromHouseholdData}
        <Grid item xs={12}>
          <BorderBox />
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Observed disabilities')}>
            {individual?.observedDisability
              .map((choice) => observedDisabilityChoicesDict[choice])
              .join(', ')}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Seeing disability severity')}>
            {severityOfDisabilityChoicesDict[individual?.seeingDisability]}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Hearing disability severity')}>
            {severityOfDisabilityChoicesDict[individual?.hearingDisability]}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Physical disability severity')}>
            {severityOfDisabilityChoicesDict[individual?.physicalDisability]}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField
            label={t('Remembering or concentrating disability severity')}
          >
            {severityOfDisabilityChoicesDict[individual?.memoryDisability]}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Self-care disability severity')}>
            {severityOfDisabilityChoicesDict[individual?.selfcareDisability]}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Communicating disability severity')}>
            {severityOfDisabilityChoicesDict[individual?.commsDisability]}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Disability')}>
            {individual?.disability === IndividualDisability.Disabled
              ? 'Disabled'
              : 'Not Disabled'}
          </LabelizedField>
        </Grid>
        {!mappedIndividualDocuments?.length &&
        !mappedIdentities?.length ? null : (
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
            {getPhoneNoLabel(individual?.phoneNo, individual?.phoneNoValid)}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Alternative Phone Number')}>
            {getPhoneNoLabel(
              individual?.phoneNoAlternative,
              individual?.phoneNoAlternativeValid,
            )}
          </LabelizedField>
        </Grid>
        <Grid item xs={12}>
          <BorderBox />
        </Grid>
        <Grid item xs={3}>
          <LabelizedField
            label={t('Date of last screening against sanctions list')}
          >
            <UniversalMoment>
              {individual?.sanctionListLastCheck}
            </UniversalMoment>
          </LabelizedField>
        </Grid>
        <Grid item xs={6}>
          {individual?.household?.unicefId && (
            <LinkedGrievancesModal
              household={individual?.household}
              baseUrl={baseUrl}
              businessArea={businessArea}
              grievancesChoices={grievancesChoices}
            />
          )}
        </Grid>
        {renderBankAccountInfo()}
        {renderDigitalWalletInfo()}
      </Grid>
    </Overview>
  );
};
