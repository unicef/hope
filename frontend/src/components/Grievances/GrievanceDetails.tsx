import { Box, Grid, Typography } from '@material-ui/core';
import React from 'react';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { ContainerColumnWithBorder } from '../ContainerColumnWithBorder';
import { LabelizedField } from '../LabelizedField';
import { OverviewContainer } from '../OverviewContainer';
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
import { GrievanceDetailsToolbar } from './GrievanceDetailsToolbar';
import { GRIEVANCE_CATEGORIES } from '../../utils/constants';
import { PaymentIds } from './PaymentIds';
import { ContentLink } from '../ContentLink';
import { OtherRelatedTickets } from './OtherRelatedTickets';

const PaddingContainer = styled.div`
  padding: 22px;
`;

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;

const RedBox = styled.div`
  padding: 30px;
  border: 3px solid red;
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

  const statusChoices: {
    [id: number]: string;
  } = reduceChoices(choicesData.grievanceTicketStatusChoices);

  const categoryChoices: {
    [id: number]: string;
  } = reduceChoices(choicesData.grievanceTicketCategoryChoices);

  const ticket = data.grievanceTicket;

  const issueType = ticket.issueType
    ? choicesData.grievanceTicketIssueTypeChoices
        .filter((el) => el.category === ticket.category.toString())[0]
        .subCategories.filter(
          (el) => el.value === ticket.issueType.toString(),
        )[0].name
    : '-';

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
    {
      label: 'Issue Type',
      value: <span>{issueType}</span>,
      size: 6,
    },
    {
      label: 'HOUSEHOLD ID',
      value: (
        <span>
          {ticket.household?.id ? (
            <ContentLink
              href={`/${businessArea}/population/household/${ticket.household.id}`}
            >
              {ticket.household.unicefId}
            </ContentLink>
          ) : (
            '-'
          )}
        </span>
      ),
      size: 3,
    },
    {
      label: 'INDIVIDUAL ID',
      value: (
        <span>
          {ticket.individual?.id ? (
            <ContentLink
              href={`/${businessArea}/population/individuals/${ticket.individual.id}`}
            >
              {ticket.individual.unicefId}
            </ContentLink>
          ) : (
            '-'
          )}
        </span>
      ),
      size: 3,
    },
    {
      label: 'PAYMENT ID',
      value: (
        <span>
          {ticket.paymentRecord?.id ? (
            <ContentLink
              href={`/${businessArea}/payment-records/${ticket.paymentRecord.id}`}
            >
              {decodeIdString(ticket.paymentRecord.id)}
            </ContentLink>
          ) : (
            '-'
          )}
        </span>
      ),
      size: 6,
    },
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
    {
      label: 'ADMINISTRATIVE LEVEL 2',
      value: <span>{ticket.admin || '-'}</span>,
      size: 3,
    },
    {
      label: 'AREA / VILLAGE / PAY POINT',
      value: <span>{ticket.area || '-'}</span>,
      size: 3,
    },
    {
      label: 'LANGUAGES SPOKEN',
      value: <span>{ticket.language}</span>,
      size: 3,
    },
  ];

  const isFeedbackType =
    ticket.category.toString() === GRIEVANCE_CATEGORIES.POSITIVE_FEEDBACK ||
    ticket.category.toString() === GRIEVANCE_CATEGORIES.NEGATIVE_FEEDBACK ||
    ticket.category.toString() === GRIEVANCE_CATEGORIES.REFERRAL;

  const renderRightSection = (): React.ReactElement => {
    if (
      ticket.category.toString() === GRIEVANCE_CATEGORIES.PAYMENT_VERIFICATION
    )
      return (
        <Box display='flex' flexDirection='column'>
          <PaymentIds ids={['34543xx', '44322xx', '12345xx']} />
          <Box mt={6}>
            <OtherRelatedTickets linkedTickets={ticket.linkedTickets.edges} />
          </Box>
        </Box>
      );
    return (
      <PaddingContainer>
        <Box display='flex' flexDirection='column'>
          <OtherRelatedTickets linkedTickets={ticket.linkedTickets.edges} />
        </Box>
      </PaddingContainer>
    );
  };

  return (
    <div>
      <GrievanceDetailsToolbar ticket={ticket} />
      <Grid container>
        <Grid item xs={12}>
          <ContainerColumnWithBorder>
            <Title>
              <Typography variant='h6'>Details</Typography>
            </Title>
            <OverviewContainer>
              <Grid container spacing={6}>
                {FieldsArray.map((el) => (
                  <Grid key={el.label} item xs={el.size}>
                    <LabelizedField label={el.label}>{el.value}</LabelizedField>
                  </Grid>
                ))}
              </Grid>
            </OverviewContainer>
          </ContainerColumnWithBorder>
        </Grid>
        <Grid item xs={7}>
          <PaddingContainer>
            <Notes notes={ticket.ticketNotes} />
          </PaddingContainer>
        </Grid>
        <Grid item xs={5}>
          {renderRightSection()}
        </Grid>
      </Grid>
    </div>
  );
}
