import { Grid, Typography } from '@material-ui/core';
import React from 'react';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { BreadCrumbsItem } from '../BreadCrumbs';
import { LabelizedField } from '../LabelizedField';
import { Missing } from '../Missing';
import { PageHeader } from '../PageHeader';
import { StatusBox } from '../StatusBox';
import { UniversalMoment } from '../UniversalMoment';
import { Notes } from './Notes';

export function GrievanceDetails(): React.ReactElement {
  const { id } = useParams();
  // const { data, loading } = useGrievancesQuery({
  //   variables: { id },
  // });
  const businessArea = useBusinessArea();
  // if (loading) {
  //   return <LoadingComponent />;
  // }

  // if (!data) {
  //   return null;
  // }
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Grievance and Feedback',
      to: `/${businessArea}/grievances-and-feedback/`,
    },
  ];
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
  const OverviewContainer = styled.div`
    display: flex;
    align-items: center;
    flex-direction: row;
  `;
  const NotesContainer = styled.div`
    padding: 22px;
  `;
  const PastContainer = styled.div`
    padding: 22px 22px 22px 0;
  `;
  const Title = styled.div`
    padding-bottom: ${({ theme }) => theme.spacing(8)}px;
  `;
  const StatusContainer = styled.div`
    min-width: 120px;
    max-width: 200px;
  `;
  const FieldsArray: {
    label: string;
    value: React.ReactElement;
    size: boolean | 3 | 6 | 8 | 11 | 'auto' | 1 | 2 | 4 | 5 | 7 | 9 | 10 | 12;
  }[] = [
    { label: 'STATUS', value: <Missing />, size: 3 },
    { label: 'CATEGORY', value: <Missing />, size: 3 },
    { label: 'HOUSEHOLD ID', value: <Missing />, size: 3 },
    { label: 'PAYMENT ID', value: <Missing />, size: 3 },
    { label: 'CONSENT', value: <Missing />, size: 3 },
    { label: 'CREATED BY', value: <Missing />, size: 3 },
    { label: 'DATE CREATED', value: <Missing />, size: 3 },
    { label: 'LAST MODIFIED DATE', value: <Missing />, size: 3 },
    { label: 'DESCRIPTION', value: <Missing />, size: 6 },
    { label: 'ASSIGNED TO', value: <Missing />, size: 6 },
    { label: 'ADMIN 2', value: <Missing />, size: 3 },
    {
      label: 'AREA / VILLAGE / PAY POINT',
      value: <Missing />,
      size: 3,
    },
    {
      label: 'LANGUAGES SPOKEN',
      value: <Missing />,
      size: 3,
    },
  ];

  const tickets: string[] = ['189-19-15311', '183-19-82649'];

  const formattedTickets = (strings: string[]) => strings.join(', ');
  return (
    <div>
      <PageHeader title={`Ticket #${id}`} breadCrumbs={breadCrumbsItems} />
      <Grid container>
        <Grid item xs={12}>
          <Container>
            <Title>
              <Typography variant='h6'>Details</Typography>
            </Title>
            <OverviewContainer>
              <Grid container spacing={6}>
                {FieldsArray.map((el) => (
                  <Grid item xs={el.size}>
                    <LabelizedField label={el.label}>{el.value}</LabelizedField>
                  </Grid>
                ))}
              </Grid>
            </OverviewContainer>
          </Container>
        </Grid>
        <Grid item xs={7}>
          <NotesContainer>
            <Notes />
          </NotesContainer>
        </Grid>
        <Grid item xs={5}>
          <PastContainer>
            <Container>
              <Title>
                <Typography variant='h6'>Past tickets</Typography>
              </Title>
              <OverviewContainer>
                <LabelizedField label='TICKET ID'>
                  <p>{formattedTickets(tickets)}</p>
                </LabelizedField>
              </OverviewContainer>
            </Container>
          </PastContainer>
        </Grid>
      </Grid>
    </div>
  );
}
