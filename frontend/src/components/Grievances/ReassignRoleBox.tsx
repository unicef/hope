import { Box, Paper, Typography } from '@material-ui/core';
import React from 'react';
import WarningIcon from '@material-ui/icons/Warning';
import styled from 'styled-components';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { GrievanceTicketQuery } from '../../__generated__/graphql';
import { LookUpReassignRole } from './LookUpReassignRole/LookUpReassignRole';
import { LabelizedField } from '../LabelizedField';
import { ContentLink } from '../ContentLink';

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

export const ReassignRoleBox = ({
  ticket,
}: {
  ticket: GrievanceTicketQuery['grievanceTicket'];
}) => {
  const businessArea = useBusinessArea();
  const householdsAndRoles = ticket?.individual?.householdsAndRoles;
  const isHeadOfHousehold =
    ticket?.individual.id === ticket?.household?.headOfHousehold?.id;
  const mappedLookUpsForExternalHouseholds = householdsAndRoles.map((el) => (
    <Box mb={2} mt={2}>
      <Box mb={2}>
        <LabelizedField label='HOUSEHOLD ID'>
          <ContentLink
            target='_blank'
            rel='noopener noreferrer'
            href={`/${businessArea}/population/household/${el.household.id}`}
          >
            {el.household.unicefId}
          </ContentLink>
        </LabelizedField>
      </Box>
      <LookUpReassignRole household={el.household} />
    </Box>
  ));

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
          <Box mb={2} mt={2}>
            <Box mb={2}>
              <LabelizedField label='HOUSEHOLD ID'>
                <ContentLink
                  target='_blank'
                  rel='noopener noreferrer'
                  href={`/${businessArea}/population/household/${ticket?.household.id}`}
                >
                  {ticket?.household.unicefId}
                </ContentLink>
              </LabelizedField>
            </Box>
            <LookUpReassignRole household={ticket?.household} />
          </Box>
        )}
        {mappedLookUpsForExternalHouseholds}
      </Box>
    </StyledBox>
  );
};
