import { Box, Grid } from '@mui/material';
import * as React from 'react';
import { GRIEVANCE_CATEGORIES, GRIEVANCE_ISSUE_TYPES } from '@utils/constants';
import { GrievanceTicketQuery } from '@generated/graphql';
import { AddIndividualGrievanceDetails } from '../AddIndividualGrievanceDetails';
import { DeleteHouseholdGrievanceDetails } from '../DeleteHouseholdGrievanceDetails';
import { DeleteIndividualGrievanceDetails } from '../DeleteIndividualGrievanceDetails';
import { FlagDetails } from '../FlagDetails';
import { NeedsAdjudicationDetailsNew } from '../NeedsAdjudication/NeedsAdjudicationDetailsNew';
import { NeedsAdjudicationDetailsOld } from '../NeedsAdjudication/NeedsAdjudicationDetailsOld';
import { PaymentGrievanceDetails } from '../PaymentGrievance/PaymentGrievanceDetails/PaymentGrievanceDetails';
import { RequestedHouseholdDataChange } from '../RequestedHouseholdDataChange';
import { RequestedIndividualDataChange } from '../RequestedIndividualDataChange';

interface GrievancesApproveSectionProps {
  ticket: GrievanceTicketQuery['grievanceTicket'];
  baseUrl: string;
  canApproveFlagAndAdjudication: boolean;
  canApproveDataChange: boolean;
  canApprovePaymentVerification: boolean;
}

export function GrievancesApproveSection({
  ticket,
  canApproveFlagAndAdjudication,
  canApproveDataChange,
  canApprovePaymentVerification,
}: GrievancesApproveSectionProps): React.ReactElement {
  const matchDetailsComponent = (): React.ReactElement => {
    if (ticket?.category?.toString() === GRIEVANCE_CATEGORIES.SYSTEM_FLAGGING) {
      return (
        <FlagDetails
          ticket={ticket}
          canApproveFlag={canApproveFlagAndAdjudication}
        />
      );
    }
    if (ticket?.category?.toString() === GRIEVANCE_CATEGORIES.NEEDS_ADJUDICATION) {
      if (ticket.needsAdjudicationTicketDetails.isMultipleDuplicatesVersion) {
        return (
          <NeedsAdjudicationDetailsNew
            ticket={ticket}
            canApprove={canApproveFlagAndAdjudication}
          />
        );
      }
      return (
        <NeedsAdjudicationDetailsOld
          ticket={ticket}
          canApprove={canApproveFlagAndAdjudication}
        />
      );
    }
    if (
      ticket?.issueType?.toString() === GRIEVANCE_ISSUE_TYPES.ADD_INDIVIDUAL
    ) {
      return (
        <AddIndividualGrievanceDetails
          ticket={ticket}
          canApproveDataChange={canApproveDataChange}
        />
      );
    }
    if (
      ticket?.issueType?.toString() === GRIEVANCE_ISSUE_TYPES.DELETE_INDIVIDUAL
    ) {
      return (
        <DeleteIndividualGrievanceDetails
          ticket={ticket}
          canApproveDataChange={canApproveDataChange}
        />
      );
    }
    if (
      ticket?.issueType?.toString() === GRIEVANCE_ISSUE_TYPES.DELETE_HOUSEHOLD
    ) {
      return (
        <DeleteHouseholdGrievanceDetails
          ticket={ticket}
          canApproveDataChange={canApproveDataChange}
        />
      );
    }
    if (
      ticket?.issueType?.toString() === GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL
    ) {
      return (
        <RequestedIndividualDataChange
          ticket={ticket}
          canApproveDataChange={canApproveDataChange}
        />
      );
    }
    if (
      ticket?.issueType?.toString() === GRIEVANCE_ISSUE_TYPES.EDIT_HOUSEHOLD
    ) {
      return (
        <RequestedHouseholdDataChange
          ticket={ticket}
          canApproveDataChange={canApproveDataChange}
        />
      );
    }
    if (
      ticket?.category?.toString() === GRIEVANCE_CATEGORIES.PAYMENT_VERIFICATION
    ) {
      if (
        ticket.paymentVerificationTicketDetails
          .hasMultiplePaymentVerifications === false
      ) {
        return (
          <PaymentGrievanceDetails
            ticket={ticket}
            canApprovePaymentVerification={canApprovePaymentVerification}
          />
        );
      }
    }
    return null;
  };

  return (
    <Grid item xs={12}>
      <Box p={3}>{matchDetailsComponent()}</Box>
    </Grid>
  );
}
