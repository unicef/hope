import { Box, Grid2 as Grid, Paper, Typography } from '@mui/material';
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
import { ContentLink } from '@core/ContentLink';
import { LabelizedField } from '@core/LabelizedField';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import { DocumentPopulationPhotoModal } from '../DocumentPopulationPhotoModal';
import { LinkedGrievancesModal } from '../LinkedGrievancesModal/LinkedGrievancesModal';
import { useProgramContext } from 'src/programContext';
import { ReactElement, ReactNode } from 'react';

const Overview = styled(Paper)`
  padding: ${({ theme }) => theme.spacing(8)}
    ${({ theme }) => theme.spacing(11)};
`;

const BorderBox = styled.div`
  border-bottom: 1px solid #e1e1e1;
`;

interface IndividualBioDataProps {
  individual: IndividualNode;
  baseUrl: string;
  businessArea: string;
  choicesData: HouseholdChoiceDataQuery;
  grievancesChoices: GrievancesChoiceDataQuery;
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
  const observedDisabilityChoicesDict = choicesToDict(
    choicesData.observedDisabilityChoices,
  );
  const severityOfDisabilityChoicesDict = choicesToDict(
    choicesData.severityOfDisabilityChoices,
  );

  const mappedIndividualDocuments = individual?.documents?.edges?.map(
    (edge) => (
      <Grid size={{ xs:3 }} key={edge.node.id}>
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
    <Grid size={{ xs:3 }} key={item.node.id}>
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

  const mappedRoles = (
    <Grid size={{ xs: 3 }}>
      <LabelizedField label={`Linked ${beneficiaryGroup?.groupLabelPlural}`}>
        {individual?.householdsAndRoles?.length
          ? individual?.householdsAndRoles?.map((item) => (
              <Box key={item.id}>
                {item.household.unicefId} -{roleChoicesDict[item.role]}
              </Box>
            ))
          : '-'}
      </LabelizedField>
    </Grid>
  );

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
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Role')}>
            {roleChoicesDict[individual?.role]}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField
            label={`Relationship to Head Of ${beneficiaryGroup?.groupLabel}`}
          >
            {relationshipChoicesDict[individual?.relationship]}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Preferred language')}>
            {individual?.preferredLanguage}
          </LabelizedField>
        </Grid>
        {mappedRoles}
        <Grid size={{ xs: 12 }}>
          <BorderBox />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField label={t('Observed disabilities')}>
            {individual?.observedDisability
              .map((choice) => observedDisabilityChoicesDict[choice])
              .join(', ')}
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
            {individual?.disability === IndividualDisability.Disabled
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
        <Grid size={{ xs:6 }}>
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
