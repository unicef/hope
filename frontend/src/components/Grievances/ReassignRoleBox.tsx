import { Box, Paper, Typography } from '@material-ui/core';
import capitalize from 'lodash/capitalize';
import React from 'react';
import WarningIcon from '@material-ui/icons/Warning';
import styled from 'styled-components';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { GrievanceTicketQuery } from '../../__generated__/graphql';
import { GRIEVANCE_CATEGORIES } from '../../utils/constants';
import { LabelizedField } from '../LabelizedField';
import { ContentLink } from '../ContentLink';
import { LookUpReassignRole } from './LookUpReassignRole/LookUpReassignRole';
import { ReassignRoleUnique } from './LookUpReassignRole/ReassignRoleUnique';

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
  shouldDisplayButton,
  shouldDisableButton,
}: {
  ticket: GrievanceTicketQuery['grievanceTicket'];
  shouldDisplayButton?: boolean;
  shouldDisableButton?: boolean;
}): React.ReactElement => {
  const businessArea = useBusinessArea();
  let { individual } = ticket;
  let { household } = ticket;
  if (ticket.category.toString() === GRIEVANCE_CATEGORIES.DEDUPLICATION) {
    individual = ticket.needsAdjudicationTicketDetails.selectedIndividual;
    household =
      ticket.needsAdjudicationTicketDetails.selectedIndividual?.household;
  }
  const householdsAndRoles = individual?.householdsAndRoles;
  const isHeadOfHousehold = individual?.id === household?.headOfHousehold?.id;
  const reassignData = JSON.parse(
    ticket.needsAdjudicationTicketDetails.roleReassignData,
  );
  const uniqueIndividual =
    ticket.needsAdjudicationTicketDetails.possibleDuplicate.id === individual.id
      ? ticket.needsAdjudicationTicketDetails.goldenRecordsIndividual
      : ticket.needsAdjudicationTicketDetails.possibleDuplicate;
  const mappedLookUpsForExternalHouseholds = householdsAndRoles
    .filter((el) => el.role !== 'NO_ROLE')
    .map((el) => (
      <Box mb={2} mt={2}>
        <Box mb={2}>
          <LabelizedField label='ROLE'>
            <>{capitalize(el.role)} Collector</>
          </LabelizedField>
          <LabelizedField label='HOUSEHOLD ID'>
            <ContentLink
              href={`/${businessArea}/population/household/${el.household.id}`}
            >
              {el.household.unicefId}
            </ContentLink>
          </LabelizedField>
        </Box>
        {shouldDisplayButton ? (
          <LookUpReassignRole
            shouldDisableButton={shouldDisableButton}
            individualRole={{ role: el.role, id: el.id }}
            ticket={ticket}
            household={el.household}
            individual={individual}
          />
        ) : null}
        {shouldDisplayButton &&
        ticket.category.toString() === GRIEVANCE_CATEGORIES.DEDUPLICATION &&
        reassignData[el.id]?.individual !== uniqueIndividual.id ? (
          <ReassignRoleUnique
            individualRole={{ role: el.role, id: el.id }}
            ticket={ticket}
            household={household}
            individual={uniqueIndividual}
          />
        ) : null}
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
              <LabelizedField label='ROLE'>
                <>Head of Household</>
              </LabelizedField>
              <LabelizedField label='HOUSEHOLD ID'>
                <ContentLink
                  href={`/${businessArea}/population/household/${ticket?.household.id}`}
                >
                  {household.unicefId}
                </ContentLink>
              </LabelizedField>
            </Box>
            {shouldDisplayButton ? (
              <LookUpReassignRole
                shouldDisableButton={shouldDisableButton}
                individualRole={{ role: 'HEAD', id: 'HEAD' }}
                ticket={ticket}
                household={household}
                individual={individual}
              />
            ) : null}
          </Box>
        )}
        {mappedLookUpsForExternalHouseholds}
      </Box>
    </StyledBox>
  );
};
