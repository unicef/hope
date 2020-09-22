import React from 'react';
import styled from 'styled-components';
import { Typography, Grid } from '@material-ui/core';
import { LabelizedField } from '../LabelizedField';
import { HouseholdNode } from '../../__generated__/graphql';
import { formatCurrency } from '../../utils/utils';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { MiśTheme } from '../../theme';
import { ContainerColumnWithBorder } from '../ContainerColumnWithBorder';

const Overview = styled.div`
  display: flex;
  flex-direction: row;
  width: 100%;
`;
const Title = styled.div`
  width: 100%;
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

const ContentLink = styled.a`
  font-family: ${({ theme }: { theme: MiśTheme }) =>
    theme.hctTypography.fontFamily};
  color: #253b46;
  font-size: 14px;
  line-height: 19px;
`;

interface HouseholdDetailsProps {
  houseHold: HouseholdNode;
}
export function HouseholdDetails({
  houseHold,
}: HouseholdDetailsProps): React.ReactElement {
  const businessArea = useBusinessArea();
  return (
    <ContainerColumnWithBorder>
      <Title>
        <Typography variant='h6'>Details</Typography>
      </Title>
      <Overview>
        <Grid container spacing={6}>
          <Grid item xs={4}>
            <LabelizedField label='Household Size'>
              <div>{houseHold.size}</div>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Country'>
              <div>{houseHold.country || '-'}</div>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Residence Status'>
              <div>{houseHold.residenceStatus}</div>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Country of Origin'>
              <div>{houseHold.countryOrigin}</div>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Head of Household'>
              <ContentLink
                href={`/${businessArea}/population/individuals/${houseHold.headOfHousehold.id}`}
              >
                {houseHold.headOfHousehold.fullName}
              </ContentLink>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Total Cash Received'>
              <div>{formatCurrency(houseHold.totalCashReceived)}</div>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='PrOgRAmmE(S) ENROLLED'>
              <div>
                {houseHold.programs.edges.map((item) => (
                  <div>{item.node.name}</div>
                ))}
              </div>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Administrative Level 1'>
              <div>{houseHold.address || '-'}</div>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Administrative Level 2'>
              <div>{houseHold.adminArea?.title || '-'}</div>
            </LabelizedField>
          </Grid>
        </Grid>
      </Overview>
    </ContainerColumnWithBorder>
  );
}
