import React from 'react';
import styled from 'styled-components';
import { Grid, Paper, Typography } from '@material-ui/core';
import { useHistory } from 'react-router-dom';
import Moment from 'react-moment';
import {
  decodeIdString,
  getAgeFromDob,
  sexToCapitalize,
} from '../../../../utils/utils';
import { ImportedIndividualDetailedFragment } from '../../../../__generated__/graphql';
import { LabelizedField } from '../../../../components/LabelizedField';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { Missing } from '../../../../components/Missing';

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
  return (
    <Overview>
      <Title>
        <Typography variant='h6'>Bio Data</Typography>
      </Title>
      <Grid container spacing={6}>
        <Grid item xs={4}>
          <LabelizedField label='Full Name'>
            <div>{individual.fullName}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='Given Name'>
            <div>{individual.givenName}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='Middle Name'>
            <div>{individual.middleName}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='Family Name'>
            <div>{individual.familyName}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='Sex'>
            <div>{sexToCapitalize(individual.sex)}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='Age'>
            <div>{age}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='Date of Birth'>
            <Moment format='DD/MM/YYYY'>{birthDate}</Moment>
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='Estimated Date of Birth'>
            <div>{individual.estimatedBirthDate ? 'YES' : 'NO'}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='ID Type'>
            <>
              Multiple id document allowed
              <Missing />
            </>
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='ID Number'>
            <>
              Multiple id document allowed
              <Missing />
            </>
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='Household ID'>
            <ContentLink onClick={() => openHousehold()}>
              {decodeIdString(individual.household.id)}
            </ContentLink>
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='Special Privileges'>
            <div>
              <Missing />
            </div>
          </LabelizedField>
        </Grid>
      </Grid>
    </Overview>
  );
}
