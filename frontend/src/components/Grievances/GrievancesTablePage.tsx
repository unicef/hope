import { Button, Grid, Typography } from '@material-ui/core';
import React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { ContainerColumnWithBorder } from '../ContainerColumnWithBorder';
import { OverviewContainer } from '../OverviewContainer';
import { PageHeader } from '../PageHeader';
import { GrievancesTable } from './GrievancesTable/GrievancesTable';

const ListContainer = styled.div`
  padding: 22px;
`;
const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

export function GrievancesTablePage(): React.ReactElement {
  const businessArea = useBusinessArea();

  return (
    <>
      <PageHeader title='Grievance and Feedback'>
        <>
          <Button
            variant='contained'
            color='primary'
            component={Link}
            to={`/${businessArea}/grievance-and-feedback/new-ticket`}
          >
            NEW TICKET
          </Button>
        </>
      </PageHeader>
      <ListContainer>
        <ContainerColumnWithBorder>
          <Title>
            <Typography variant='h6'>Grievance and Feedback List</Typography>
          </Title>
          <OverviewContainer>
            <Grid container spacing={6}>
              <GrievancesTable businessArea={businessArea} />
            </Grid>
          </OverviewContainer>
        </ContainerColumnWithBorder>
      </ListContainer>
    </>
  );
}
