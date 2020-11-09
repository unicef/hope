import { Grid, Typography } from '@material-ui/core';
import React from 'react';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { BreadCrumbsItem } from '../BreadCrumbs';
import { ContainerColumnWithBorder } from '../ContainerColumnWithBorder';
import { LabelizedField } from '../LabelizedField';
import { Missing } from '../Missing';
import { OverviewContainer } from '../OverviewContainer';
import { PageHeader } from '../PageHeader';
import {
  decodeIdString,
  grievanceTicketStatusToColor,
  reduceChoices,
  renderUserName,
} from '../../utils/utils';
import { LoadingComponent } from '../LoadingComponent';
import {
  useGrievancesChoiceDataQuery,
  useGrievanceTicketQuery,
} from '../../__generated__/graphql';
import { StatusBox } from '../StatusBox';
import { UniversalMoment } from '../UniversalMoment';
import { Notes } from './Notes';
import { PastTickets } from './PastTickets';

const NotesContainer = styled.div`
  padding: 22px;
`;

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;

export function GrievanceDetails(): React.ReactElement {
  const { id } = useParams();
  const { data, loading } = useGrievanceTicketQuery({
    variables: { id },
  });
  const businessArea = useBusinessArea();

  const {
    data: choicesData,
    loading: choicesLoading,
  } = useGrievancesChoiceDataQuery();
  if (choicesLoading) {
    return null;
  }
  if (loading || choicesLoading) {
    return <LoadingComponent />;
  }

  if (!data || !choicesData) {
    return null;
  }
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Grievance and Feedback',
      to: `/${businessArea}/grievance-and-feedback/`,
    },
  ];

  const statusChoices: {
    [id: number]: string;
  } = reduceChoices(choicesData.grievanceTicketStatusChoices);

  const categoryChoices: {
    [id: number]: string;
  } = reduceChoices(choicesData.grievanceTicketCategoryChoices);

  const ticket = data.grievanceTicket;

  const FieldsArray: {
    label: string;
    value: React.ReactElement;
    size: boolean | 3 | 6 | 8 | 11 | 'auto' | 1 | 2 | 4 | 5 | 7 | 9 | 10 | 12;
  }[] = [
    {
      label: 'STATUS',
      value: (
        <StatusContainer>
          <StatusBox
            status={statusChoices[ticket.status]}
            statusToColor={grievanceTicketStatusToColor}
          />
        </StatusContainer>
      ),
      size: 3,
    },
    {
      label: 'CATEGORY',
      value: <span>{categoryChoices[ticket.category]}</span>,
      size: 3,
    },
    { label: 'HOUSEHOLD ID', value: <Missing />, size: 3 },
    { label: 'PAYMENT ID', value: <Missing />, size: 3 },
    {
      label: 'CONSENT',
      value: <span>{ticket.consent ? 'Yes' : 'No'}</span>,
      size: 3,
    },
    {
      label: 'CREATED BY',
      value: <span>{renderUserName(ticket.createdBy)}</span>,
      size: 3,
    },
    {
      label: 'DATE CREATED',
      value: <UniversalMoment>{ticket.createdAt}</UniversalMoment>,
      size: 3,
    },
    {
      label: 'LAST MODIFIED DATE',
      value: <UniversalMoment>{ticket.updatedAt}</UniversalMoment>,
      size: 3,
    },
    { label: 'DESCRIPTION', value: <span>{ticket.description}</span>, size: 6 },
    {
      label: 'ASSIGNED TO',
      value: <span>{renderUserName(ticket.assignedTo)}</span>,
      size: 6,
    },
    { label: 'ADMIN 2', value: <Missing />, size: 3 },
    {
      label: 'AREA / VILLAGE / PAY POINT',
      value: <Missing />,
      size: 3,
    },
    {
      label: 'LANGUAGES SPOKEN',
      value: <span>{ticket.language}</span>,
      size: 3,
    },
  ];

  const tickets: string[] = ['189-19-15311', '183-19-82649'];

  return (
    <div>
      <PageHeader
        title={`Ticket #${decodeIdString(id)}`}
        breadCrumbs={breadCrumbsItems}
      />
      <Grid container>
        <Grid item xs={12}>
          <ContainerColumnWithBorder>
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
          </ContainerColumnWithBorder>
        </Grid>
        <Grid item xs={7}>
          <NotesContainer>
            <Notes />
          </NotesContainer>
        </Grid>
        <Grid item xs={5}>
          <PastTickets tickets={tickets} />
        </Grid>
      </Grid>
    </div>
  );
}
