import React from 'react';
import styled from 'styled-components';
import { Paper, Typography, Grid } from '@material-ui/core';
import { LabelizedField } from '../LabelizedField';
import { IndividualNode } from '../../__generated__/graphql';
import { useHistory } from 'react-router-dom';
import {
  getAgeFromDob,
  sexToCapitalize,
  getIdentificationType, decodeIdString,
} from '../../utils/utils';
import Moment from 'react-moment';
import { useBusinessArea } from '../../hooks/useBusinessArea';

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

interface IndividualBioDataProps {
  individual: IndividualNode;
}
export function IndividualsBioData({
  individual,
}: IndividualBioDataProps): React.ReactElement {
  const history = useHistory();
  const businessArea = useBusinessArea();

  let age: number | null;
  const { dob } = individual;
  if (dob) {
    age = getAgeFromDob(dob);
  }

  const openHousehold = (): void => {
    history.push(
      `/${businessArea}/population/household/${individual.household.id}`,
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
            <div>{individual.firstName}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='Middle Name'>
            <div>-</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='Family Name'>
            <div>{individual.lastName}</div>
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
            <Moment format='DD/MM/YYYY'>{dob}</Moment>
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='Estimated Date of Birth'>
            <div>
              {individual.estimatedDob ? individual.estimatedDob : 'No'}
            </div>
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='ID Type'>
            <div>{getIdentificationType(individual.identificationType)}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='ID Number'>
            <div>{individual.identificationNumber}</div>
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
            <div>-</div>
          </LabelizedField>
        </Grid>
      </Grid>
    </Overview>
  );
}
