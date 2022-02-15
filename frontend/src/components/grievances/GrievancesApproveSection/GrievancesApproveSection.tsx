import { Box, Grid } from '@material-ui/core';
import React from 'react';
import {
  GRIEVANCE_CATEGORIES,
  GRIEVANCE_ISSUE_TYPES,
} from '../../../utils/constants';

import { GrievanceTicketQuery } from '../../../__generated__/graphql';
import { AddIndividualGrievanceDetails } from '../AddIndividualGrievanceDetails';
import { DeleteHouseholdGrievanceDetails } from '../DeleteHouseholdGrievanceDetails';
import { DeleteIndividualGrievanceDetails } from '../DeleteIndividualGrievanceDetails';
import { FlagDetails } from '../FlagDetails';
import { NeedsAdjudicationDetails } from '../NeedsAdjudicationDetails';
import { RequestedHouseholdDataChange } from '../RequestedHouseholdDataChange';
import { RequestedIndividualDataChange } from '../RequestedIndividualDataChange';

interface GrievancesApproveSectionProps {
  ticket: GrievanceTicketQuery['grievanceTicket'];
  businessArea: string;
  canApproveFlagAndAdjudication: boolean;
  canApproveDataChange: boolean;
}

export function GrievancesApproveSection({
  ticket,
  canApproveFlagAndAdjudication,
  canApproveDataChange,
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
    if (ticket?.category?.toString() === GRIEVANCE_CATEGORIES.DEDUPLICATION) {
      <NeedsAdjudicationDetails
        ticket={ticket}
        canApprove={canApproveFlagAndAdjudication}
      />;
    }
    if (
      ticket?.issueType?.toString() === GRIEVANCE_ISSUE_TYPES.ADD_INDIVIDUAL
    ) {
      <AddIndividualGrievanceDetails
        ticket={ticket}
        canApproveDataChange={canApproveDataChange}
      />;
    }
    if (
      ticket?.issueType?.toString() === GRIEVANCE_ISSUE_TYPES.DELETE_INDIVIDUAL
    ) {
      <DeleteIndividualGrievanceDetails
        ticket={ticket}
        canApproveDataChange={canApproveDataChange}
      />;
    }
    if (
      ticket?.issueType?.toString() === GRIEVANCE_ISSUE_TYPES.DELETE_HOUSEHOLD
    ) {
      <DeleteHouseholdGrievanceDetails
        ticket={ticket}
        canApproveDataChange={canApproveDataChange}
      />;
    }
    if (
      ticket?.issueType?.toString() === GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL
    ) {
      <RequestedIndividualDataChange
        ticket={ticket}
        canApproveDataChange={canApproveDataChange}
      />;
    }
    if (
      ticket?.issueType?.toString() === GRIEVANCE_ISSUE_TYPES.EDIT_HOUSEHOLD
    ) {
      <RequestedHouseholdDataChange
        ticket={ticket}
        canApproveDataChange={canApproveDataChange}
      />;
    }
  };

  return (
    <Grid item xs={12}>
      <Box p={4}>{matchDetailsComponent()}</Box>
    </Grid>
  );
}
