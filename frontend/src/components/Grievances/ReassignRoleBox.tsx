import { Box, Paper, Typography } from '@material-ui/core';
import React, { useState } from 'react';
import WarningIcon from '@material-ui/icons/Warning';
import styled from 'styled-components';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { decodeIdString } from '../../utils/utils';
import {
  GrievanceTicketQuery,
  useExistingGrievanceTicketsQuery,
} from '../../__generated__/graphql';

import { LoadingComponent } from '../LoadingComponent';
import { LookUpReassignRole } from './LookUpReassignRole/LookUpReassignRole';
import { Formik } from 'formik';

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

  const householdsAndRoles = ticket?.individual?.householdsAndRoles;
  console.log('😎: householdsAndRoles', householdsAndRoles);

  const isHeadOfHousehold =
    ticket?.individual.id === ticket?.household?.headOfHousehold?.id;

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
        {isHeadOfHousehold && (
          <LookUpReassignRole household={ticket?.household} />
        )}
      </Box>
    </StyledBox>
  );
};
