import { Box, Grid2 as Grid } from '@mui/material';
import { isEmpty } from 'lodash';
import {
  GRIEVANCE_CATEGORIES,
  GRIEVANCE_ISSUE_TYPES,
  GRIEVANCE_TICKET_STATES,
} from '@utils/constants';
import { OtherRelatedTickets } from '../OtherRelatedTickets';
import { PaymentIds } from '../PaymentIds';
import { ReassignMultipleRoleBox } from '../ReassignMultipleRoleBox';
import { ReassignRoleBox } from '../ReassignRoleBox';
import { ReactElement } from 'react';
import { useProgramContext } from 'src/programContext';
import { GrievanceTicketDetail } from '@restgenerated/models/GrievanceTicketDetail';

export function GrievancesSidebar({
  ticket,
}: {
  ticket: GrievanceTicketDetail;
}): ReactElement {
  const { isSocialDctType } = useProgramContext();
  const shouldShowReassignBoxDataChange = (): boolean => {
    let { individual, household } = ticket;
    const { category, issueType, status } = ticket;

    if (category.toString() === GRIEVANCE_CATEGORIES.NEEDS_ADJUDICATION) {
      individual = ticket.ticketDetails.selectedIndividual;
      household = ticket.ticketDetails.selectedIndividual?.household;
    }
    const isOneIndividual = household?.activeIndividualsCount === 1;
    if (isOneIndividual) return false;

    const isRightCategory = [
      {
        category: GRIEVANCE_CATEGORIES.DATA_CHANGE,
        issueType: GRIEVANCE_ISSUE_TYPES.DELETE_INDIVIDUAL,
      },
      {
        category: GRIEVANCE_CATEGORIES.DATA_CHANGE,
        issueType: GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL,
      },
      {
        category: GRIEVANCE_CATEGORIES.SYSTEM_FLAGGING,
        issueType: undefined,
        approveStatus: ticket?.ticketDetails?.approveStatus,
      },
      {
        category: GRIEVANCE_CATEGORIES.NEEDS_ADJUDICATION,
        selectedIndividual: ticket?.ticketDetails?.selectedIndividual,
      },
    ].some(
      (condition) =>
        category.toString() === condition.category &&
        (issueType?.toString() === condition.issueType ||
          condition.approveStatus ||
          condition.selectedIndividual),
    );

    if (!isRightCategory) return false;

    const isRightStatus = status === GRIEVANCE_TICKET_STATES.FOR_APPROVAL;
    if (!isRightStatus) return false;

    const rolesInHouseholds = individual?.rolesInHouseholds || [];
    const isHeadOfHousehold = individual?.id === household?.headOfHousehold?.id;
    const hasRolesToReassign = rolesInHouseholds.some(
      (el) => el.role !== 'NO_ROLE',
    );

    let isProperDataChange = true;
    if (
      category.toString() === GRIEVANCE_CATEGORIES.DATA_CHANGE &&
      issueType.toString() === GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL
    ) {
      const { role, relationship } = ticket.ticketDetails.individualData;
      if (isEmpty(role) && isEmpty(relationship)) {
        isProperDataChange = false;
      }
    }

    return (
      (isHeadOfHousehold || hasRolesToReassign) &&
      isProperDataChange &&
      !isSocialDctType
    );
  };

  const shouldShowReassignMultipleBoxDataChange = (): boolean =>
    ticket.category.toString() === GRIEVANCE_CATEGORIES.NEEDS_ADJUDICATION &&
    ticket.ticketDetails.isMultipleDuplicatesVersion &&
    !isSocialDctType;

  const renderRightSection = (): ReactElement => {
    if (
      ticket.category.toString() === GRIEVANCE_CATEGORIES.PAYMENT_VERIFICATION
    ) {
      return (
        <Box display="flex" flexDirection="column">
          <Box mt={3}>
            {ticket.ticketDetails?.hasMultiplePaymentVerifications ? (
              <PaymentIds
                verifications={
                  ticket.ticketDetails?.paymentVerifications.map((edge) => ({
                    id: edge.id,
                    paymentId: ticket.paymentRecord.unicefId,
                  })) || []
                }
              />
            ) : null}
          </Box>
          <Box mt={3}>
            <OtherRelatedTickets ticket={ticket} />
          </Box>
        </Box>
      );
    }
    if (shouldShowReassignBoxDataChange()) {
      return (
        <Box p={3}>
          <Box display="flex" flexDirection="column">
            <ReassignRoleBox
              shouldDisplayButton
              shouldDisableButton={ticket.ticketDetails?.approveStatus}
              ticket={ticket}
            />
          </Box>
        </Box>
      );
    }

    if (shouldShowReassignMultipleBoxDataChange()) {
      return (
        <Box p={3}>
          <Box display="flex" flexDirection="column">
            <ReassignMultipleRoleBox ticket={ticket} />
          </Box>
        </Box>
      );
    }

    return (
      <Box p={3}>
        <Box display="flex" flexDirection="column">
          <OtherRelatedTickets ticket={ticket} />
        </Box>
      </Box>
    );
  };

  return <Grid size={{ xs: 4 }}>{renderRightSection()}</Grid>;
}
