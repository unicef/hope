import { Button, Grid, Typography } from '@material-ui/core';
import React from 'react';
import { Link, useParams } from 'react-router-dom';
import styled from 'styled-components';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { ContainerColumnWithBorder } from '../ContainerColumnWithBorder';
import { Missing } from '../Missing';
import { OverviewContainer } from '../OverviewContainer';
import { PageHeader } from '../PageHeader';
import { StatusBox } from '../StatusBox';

export function GrievancesList(): React.ReactElement {
  const { id } = useParams();
  // const { data, loading } = useGrievancesQuery({
  //   variables: { id },
  // });
  const businessArea = useBusinessArea();

  const ListContainer = styled.div`
    padding: 22px;
  `;
  const Title = styled.div`
    padding-bottom: ${({ theme }) => theme.spacing(8)}px;
  `;
  const StatusContainer = styled.div`
    min-width: 120px;
    max-width: 200px;
  `;

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
              table goes here
            </Grid>
          </OverviewContainer>
        </ContainerColumnWithBorder>
      </ListContainer>
    </>
  );
}
