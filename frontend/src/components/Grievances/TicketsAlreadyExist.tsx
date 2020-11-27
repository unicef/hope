import { Box, Paper, Typography } from '@material-ui/core';
import WarningIcon from '@material-ui/icons/Warning';
import React from 'react';
import styled from 'styled-components';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { decodeIdString } from '../../utils/utils';
import { useExistingGrievanceTicketsQuery } from '../../__generated__/graphql';
import { ContentLink } from '../ContentLink';
import { LoadingComponent } from '../LoadingComponent';

const StyledBox = styled(Paper)`
  border: 1px solid ${({ theme }) => theme.hctPalette.oragne};
  border-radius: 3px;
  background-color: #fff;
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 26px 22px;
`;
const Title = styled.div`
  color: ${({ theme }) => theme.hctPalette.oragne};
`;

const WarnIcon = styled(WarningIcon)`
  position: relative;
  top: 5px;
  margin-right: 10px;
`;

export const TicketsAlreadyExist = ({ values }) => {
  const businessArea = useBusinessArea();

  const { data, loading } = useExistingGrievanceTicketsQuery({
    variables: {
      businessArea,
      category: values.category,
      issueType: values.issueType,
      household: decodeIdString(values.selectedHousehold?.id),
      individual: decodeIdString(values.selectedIndividual?.id),
      paymentRecord: values.selectedPaymentRecords,
    },
  });
  if (loading) return <LoadingComponent />;
  if (!data) return null;
  const { edges } = data.existingGrievanceTickets;
  const mappedTickets = edges?.map((edge) => (
    <Box mb={2}>
      <ContentLink
        target='_blank'
        rel='noopener noreferrer'
        href={`/${businessArea}/grievance-and-feedback/${edge.node.id}`}
      >
        {decodeIdString(edge.node.id)}
      </ContentLink>
    </Box>
  ));
  return edges.length ? (
    <StyledBox>
      <Title>
        <Typography variant='h6'>
          <WarnIcon />
          {edges.length === 1
            ? 'Ticket already exists'
            : 'Tickets already exist'}
        </Typography>
      </Title>
      <Typography variant='body2'>
        There is an open ticket(s) in the same category for the related entity.
        Please review them before proceeding.
      </Typography>
      <Box mt={3} display='flex' flexDirection='column'>
        {mappedTickets}
      </Box>
    </StyledBox>
  ) : null;
};
