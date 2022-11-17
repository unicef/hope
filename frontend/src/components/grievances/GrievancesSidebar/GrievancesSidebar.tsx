import { Box, Grid } from '@material-ui/core';
import { isEmpty } from 'lodash';
import React from 'react';
import {
  GRIEVANCE_CATEGORIES,
  GRIEVANCE_ISSUE_TYPES,
  GRIEVANCE_TICKET_STATES,
} from '../../../utils/constants';
import { OtherRelatedTickets } from '../OtherRelatedTickets';
import { PaymentIds } from '../PaymentIds';
import { ReassignMultipleRoleBox } from '../ReassignMultipleRoleBox';
import { ReassignRoleBox } from '../ReassignRoleBox';
import { GrievanceTicketNode } from '../../../__generated__/graphql';

export const GrievancesSidebar = ({ ticket }: { ticket: GrievanceTicketNode }): React.ReactElement => {
  const shouldShowReassignBoxDataChange = (): boolean => {
    let { individual, household } = ticket;
    const { category, issueType, status } = ticket;
    if (category.toString() === GRIEVANCE_CATEGORIES.DEDUPLICATION) {
      individual = ticket.needsAdjudicationTicketDetails.selectedIndividual;
      household =
        ticket.needsAdjudicationTicketDetails.selectedIndividual?.household;
    }
    const isOneIndividual = household?.activeIndividualsCount === 1;

    if (isOneIndividual) return false;
    const isRightCategory =
      (category.toString() === GRIEVANCE_CATEGORIES.DATA_CHANGE &&
        issueType.toString() === GRIEVANCE_ISSUE_TYPES.DELETE_INDIVIDUAL) ||
      (category.toString() === GRIEVANCE_CATEGORIES.DATA_CHANGE &&
        issueType.toString() === GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL) ||
      (category.toString() === GRIEVANCE_CATEGORIES.SYSTEM_FLAGGING &&
        ticket?.systemFlaggingTicketDetails?.approveStatus) ||
      (category.toString() === GRIEVANCE_CATEGORIES.DEDUPLICATION &&
        ticket?.needsAdjudicationTicketDetails?.selectedIndividual);

    if (!isRightCategory) return false;

    const isRightStatus = status === GRIEVANCE_TICKET_STATES.FOR_APPROVAL;
    if (!isRightStatus) return false;

    const householdsAndRoles = individual?.householdsAndRoles;
    const isHeadOfHousehold = individual?.id === household?.headOfHousehold?.id;
    const hasRolesToReassign =
      householdsAndRoles?.filter((el) => el.role !== 'NO_ROLE').length > 0;

    let isProperDataChange = true;
    if (
      category.toString() === GRIEVANCE_CATEGORIES.DATA_CHANGE &&
      issueType.toString() === GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL
    ) {
      if (
        isEmpty(ticket.individualDataUpdateTicketDetails.individualData.role) &&
        isEmpty(
          ticket.individualDataUpdateTicketDetails.individualData.relationship,
        )
      ) {
        isProperDataChange = false;
      }
    }

    return (isHeadOfHousehold || hasRolesToReassign) && isProperDataChange;
  };

  const shouldShowReassignMultipleBoxDataChange = (): boolean =>
    ticket.category.toString() === GRIEVANCE_CATEGORIES.DEDUPLICATION &&
    ticket.needsAdjudicationTicketDetails.isMultipleDuplicatesVersion;

  const renderRightSection = (): React.ReactElement => {
    if (
      ticket.category.toString() === GRIEVANCE_CATEGORIES.PAYMENT_VERIFICATION
    )
      return (
        <Box display='flex' flexDirection='column'>
          <Box mt={3}>
            {ticket.paymentVerificationTicketDetails
              ?.hasMultiplePaymentVerifications ? (
              <PaymentIds
                verifications={
                  ticket.paymentVerificationTicketDetails?.paymentVerifications
                    ?.edges.map((edge) => ({ "id": edge.node.id, "caId": ticket.paymentRecord.caId })) || []
                }
              />
            ) : null}
          </Box>
          <Box mt={3}>
            <OtherRelatedTickets
              ticket={ticket}
              linkedTickets={ticket.relatedTickets}
            />
          </Box>
        </Box>
      );
    if (shouldShowReassignBoxDataChange()) {
      return (
        <Box p={3}>
          <Box display='flex' flexDirection='column'>
            <ReassignRoleBox
              shouldDisplayButton
              shouldDisableButton={
                ticket.deleteIndividualTicketDetails?.approveStatus
              }
              ticket={ticket}
            />
          </Box>
        </Box>
      );
    }

    if (shouldShowReassignMultipleBoxDataChange()) {
      return (
        <Box p={3}>
          <Box display='flex' flexDirection='column'>
            <ReassignMultipleRoleBox ticket={ticket} />
          </Box>
        </Box>
      );
    }

    return (
      <Box p={3}>
        <Box display='flex' flexDirection='column'>
          <OtherRelatedTickets
            ticket={ticket}
            linkedTickets={ticket.relatedTickets}
          />
        </Box>
      </Box>
    );
  };

  return (
    <Grid item xs={3}>
      {renderRightSection()}
    </Grid>
  );
};
