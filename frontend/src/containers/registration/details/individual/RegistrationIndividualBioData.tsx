import React from 'react';
import styled from 'styled-components';
import { Grid, Paper, Typography } from '@material-ui/core';
import { useHistory } from 'react-router-dom';
import {
  decodeIdString,
  getAgeFromDob,
  sexToCapitalize,
  choicesToDict,
} from '../../../../utils/utils';
import {
  ImportedIndividualDetailedFragment,
  useHouseholdChoiceDataQuery,
} from '../../../../__generated__/graphql';
import { LabelizedField } from '../../../../components/LabelizedField';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { LoadingComponent } from '../../../../components/LoadingComponent';
import { UniversalMoment } from '../../../../components/UniversalMoment';

const Overview = styled(Paper)`
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
`;

const Title = styled.div`
  width: 100%;
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

const ContentLink = styled.div`
  text-decoration: underline;
  cursor: pointer;
`;

interface RegistrationIndividualBioDataProps {
  individual: ImportedIndividualDetailedFragment;
}
export function RegistrationIndividualsBioData({
  individual,
}: RegistrationIndividualBioDataProps): React.ReactElement {
  const history = useHistory();
  const businessArea = useBusinessArea();

  let age: number | null;
  const { birthDate } = individual;
  if (birthDate) {
    age = getAgeFromDob(birthDate);
  }

  const openHousehold = (): void => {
    history.push(
      `/${businessArea}/registration-data-import/household/${individual.household.id}`,
    );
  };
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useHouseholdChoiceDataQuery();

  if (choicesLoading) {
    return <LoadingComponent />;
  }
  const relationshipChoicesDict = choicesToDict(
    choicesData.relationshipChoices,
  );
  const maritalStatusChoicesDict = choicesToDict(
    choicesData.maritalStatusChoices,
  );
  const roleChoicesDict = choicesToDict(choicesData.roleChoices);
  const mappedIndividualDocuments = individual.documents?.edges?.map((edge) => (
    <Grid item xs={3}>
      <LabelizedField label={edge.node.type.label}>
        <div>{edge.node.documentNumber}</div>
      </LabelizedField>
    </Grid>
  ));
  const mappedIdentities = individual.identities?.map((item) => (
    <Grid item xs={3}>
      <LabelizedField label={`${item.type} ID`}>
        <div>{item.documentNumber}</div>
      </LabelizedField>
    </Grid>
  ));

  return (
    <Overview>
      <Title>
        <Typography variant='h6'>Bio Data</Typography>
      </Title>
      <Grid container spacing={6}>
        <Grid item xs={3}>
          <LabelizedField label='Full Name'>
            <div>{individual.fullName}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Given Name'>
            <div>{individual.givenName}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Middle Name'>
            <div>{individual.middleName || '-'}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Family Name'>
            <div>{individual.familyName}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Gender'>
            <div>{sexToCapitalize(individual.sex)}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Age'>
            <div>{age}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Date of Birth'>
            <UniversalMoment>{birthDate}</UniversalMoment>
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Estimated Date of Birth'>
            <div>
              {individual.estimatedBirthDate
                ? individual.estimatedBirthDate
                : 'No'}
            </div>
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Phone Number'>
            <div>{individual.phoneNo}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Alternate Phone Number'>
            <div>{individual.phoneNoAlternative || '-'}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Household ID'>
            <ContentLink onClick={() => openHousehold()}>
              {decodeIdString(individual.household.id)}
            </ContentLink>
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Role'>
            <div>{roleChoicesDict[individual.role]}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Relationship to HOH'>
            <div>{relationshipChoicesDict[individual.relationship]}</div>
          </LabelizedField>
        </Grid>
        {mappedIndividualDocuments}
        {mappedIdentities}
        <Grid item xs={3}>
          <LabelizedField label='Marital Status'>
            <div>{maritalStatusChoicesDict[individual.maritalStatus]}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label='Pregnant'>
            <div>
              <div>{individual.pregnant ? 'Yes' : 'No' || '-'}</div>
            </div>
          </LabelizedField>
        </Grid>
      </Grid>
    </Overview>
  );
}
