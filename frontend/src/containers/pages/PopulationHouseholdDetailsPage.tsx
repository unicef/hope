import React from 'react';
import styled from 'styled-components';
import Paper from '@material-ui/core/Paper';
import ExpandLess from '@material-ui/icons/ExpandLess';
import ExpandMore from '@material-ui/icons/ExpandMore';
import { Typography, Button } from '@material-ui/core';
import { useParams } from 'react-router-dom';
import { HouseholdDetails } from '../../components/population/HouseholdDetails';
import { PageHeader } from '../../components/PageHeader';
import { useHouseholdQuery, HouseholdNode } from '../../__generated__/graphql';
import { BreadCrumbsItem } from '../../components/BreadCrumbs';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { HouseholdVulnerabilities } from '../../components/population/HouseholdVulnerabilities';

const Container = styled.div`
padding 20px;
  && {
    display: flex;
    flex-direction: column;
    width: 100%;
  }
`;

const Title = styled.div`
  width: 100%;
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

const Overview = styled(Paper)`
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
  margin-top: 20px;
  &:first-child {
    margin-top: 0px;
  }
`;

const ButtonContainer = styled.span`
  margin: 0 ${({ theme }) => theme.spacing(2)}px;
  float: right;
`;

export function PopulationHouseholdDetailsPage(): React.ReactElement {
  const { id } = useParams();
  const businessArea = useBusinessArea();
  const { data, loading } = useHouseholdQuery({
    variables: { id },
  });

  if (loading) return null;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Household Details',
      to: `/${businessArea}/population/household`,
    },
  ];

  return (
    <div>
      <PageHeader
        title={`Household ID: ${id}`}
        breadCrumbs={breadCrumbsItems}
      />
      <HouseholdDetails houseHold={data.household as HouseholdNode} />
      <Container>
        <HouseholdVulnerabilities />
        <Overview>
          <Title>
            <Typography variant='h6' style={{ display: 'inline-block' }}>
              Activity Log
            </Typography>
            <ButtonContainer>
              <Button
                variant='outlined'
                color='primary'
                startIcon={<ExpandMore />}
              >
                Show
              </Button>
            </ButtonContainer>
          </Title>
        </Overview>
      </Container>
    </div>
  );
}
