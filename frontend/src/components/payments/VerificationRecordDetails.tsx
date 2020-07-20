import React, { useState } from 'react';
import styled from 'styled-components';
import { Grid, Typography, Box, Paper } from '@material-ui/core';
import { Doughnut } from 'react-chartjs-2';
import { useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { PageHeader } from '../PageHeader';
import { LabelizedField } from '../LabelizedField';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { BreadCrumbsItem } from '../BreadCrumbs';
import { UniversalActivityLogTable } from '../../containers/tables/UniversalActivityLogTable';
import { useCashPlanQuery } from '../../__generated__/graphql';
import { LoadingComponent } from '../LoadingComponent';
import { Missing } from '../Missing';

const Container = styled.div`
  display: flex;
  flex: 1;
  width: 100%;
  background-color: #fff;
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
  flex-direction: column;
  border-color: #b1b1b5;
  border-bottom-width: 1px;
  border-bottom-style: solid;
`;

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

const Overview = styled(Paper)`
  margin: 20px;
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
`;

const TableWrapper = styled.div`
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  padding: 20px;
  padding-bottom: 0;
`;
const StatusContainer = styled.div`
  width: 120px;
`;
// interface PaymentVerificationDetailsProps {
//   registration: 'registr';
// }

export function VerificationRecordDetails(): React.ReactElement {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const { id } = useParams();
  const { data, loading } = useCashPlanQuery({
    variables: { id },
  });
  // if (loading) {
  //   return <LoadingComponent />;
  // }
  // if (!data) {
  //   return null;
  // }

  // const { cashPlan } = data;
  // const verificationPlan = cashPlan.verifications.edges.length
  //   ? cashPlan.verifications.edges[0].node
  //   : null;

  return (
    <>
      <Container>
        <Title>
          <Typography variant='h6'>Payment Record Details</Typography>
        </Title>
        <Grid container spacing={3}>
          <Grid item xs={3}>
            <LabelizedField label='STATUS'>
              <Missing />
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label='STATUS DATE'>
              <Missing />
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label='REGISTRATION GROUP'>
              <Missing />
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label='TARGET POPULATION'>
              <Missing />
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label='DISTRIBUTION MODALITY'>
              <Missing />
            </LabelizedField>
          </Grid>
        </Grid>
      </Container>
      <Container>
        <Title>
          <Typography variant='h6'>Verification Details</Typography>
        </Title>
        <Grid container spacing={3}>
          <Grid item xs={3}>
            <LabelizedField label='STATUS'>
              <Missing />
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label='STATUS DATE'>
              <Missing />
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label='AMOUNT RECEIVED'>
              <Missing />
            </LabelizedField>
          </Grid>
        </Grid>
      </Container>
      <Overview>
        <Title>
          <Typography variant='h6'>Household</Typography>
        </Title>
        <Grid container spacing={3}>
          <Grid item xs={3}>
            <LabelizedField label='HOUSEHOLD ID'>
              <Missing />
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label='HEAD OF HOUSEHOLD'>
              <Missing />
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label='TOTAL PERSON COVERED'>
              <Missing />
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label='PHONE NUMBER'>
              <Missing />
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label='ALT. PHONE NUMBER'>
              <Missing />
            </LabelizedField>
          </Grid>
        </Grid>
      </Overview>
      <Overview>
        <Title>
          <Typography variant='h6'>Entitlement Details</Typography>
        </Title>
        <Grid container spacing={3}>
          <Grid item xs={3}>
            <LabelizedField label='ENTITLEMENT QUANTITY'>
              <Missing />
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label='DELIVERED QUANTITY'>
              <Missing />
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label='CURRENCY'>
              <Missing />
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label='DELIVERY TYPE'>
              <Missing />
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label='DELIVERY DATE'>
              <Missing />
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label='ENTITLEMENT CARD ID'>
              <Missing />
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label='TRANSACTION REFERENCE ID'>
              <Missing />
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label='ENTITLEMENT CARD ISSUE DATE'>
              <Missing />
            </LabelizedField>
          </Grid>
          <Grid item xs={3}>
            <LabelizedField label='FSP'>
              <Missing />
            </LabelizedField>
          </Grid>
        </Grid>
      </Overview>
      <TableWrapper>
        <UniversalActivityLogTable objectId='some id' />
      </TableWrapper>
    </>
    //connect it later
  );
}
