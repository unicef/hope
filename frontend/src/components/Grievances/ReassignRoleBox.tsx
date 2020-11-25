import { Box, Grid, Paper, Typography } from '@material-ui/core';
import React, { useState } from 'react';
import WarningIcon from '@material-ui/icons/Warning';
import styled from 'styled-components';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { GRIEVANCE_TICKET_STATES } from '../../utils/constants';
import { decodeIdString } from '../../utils/utils';
import {
  GrievanceTicketQuery,
  useExistingGrievanceTicketsQuery,
} from '../../__generated__/graphql';
import { ContentLink } from '../ContentLink';
import { LabelizedField } from '../LabelizedField';
import { LoadingComponent } from '../LoadingComponent';
import { Missing } from '../Missing';

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

const BlueBold = styled.div`
  color: ${({ theme }) => theme.hctPalette.navyBlue};
  font-weight: 500;
  cursor: pointer;
`;
const WarnIcon = styled(WarningIcon)`
  position: relative;
  top: 5px;
  margin-right: 10px;
`;

export const ReassignRoleBox = ({
                                  ticket,
                                }: {
  ticket: GrievanceTicketQuery['grievanceTicket'];
}) => {
  const businessArea = useBusinessArea();
  const [show, setShow] = useState(false);

  const { data, loading } = useExistingGrievanceTicketsQuery({
    variables: {
      businessArea,
      household:
        decodeIdString(ticket.household?.id) ||
        '294cfa7e-b16f-4331-8014-a22ffb2b8b3c',
      //adding some random ID to get 0 results if there is no household id.
    },
  });
  if (loading) return <LoadingComponent />;
  if (!data) return null;

  const householdTickets = data.existingGrievanceTickets.edges;

  const households = ['HH-1', 'HH-2', 'HH-3'];

  return (
    <StyledBox>
      <Title>
        <Typography variant='h6'>
          <WarnIcon />
          Individual is the HOH or the external collector for a household
        </Typography>
      </Title>
      <Typography variant='body2'>
        Upon removing you will need to select new individual(s) for this role.
      </Typography>
      <Box mt={3} display='flex' flexDirection='column'>
        <Missing />
      </Box>
    </StyledBox>
  );
};
