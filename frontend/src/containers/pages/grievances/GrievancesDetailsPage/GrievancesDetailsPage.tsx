import { Box, Grid } from '@material-ui/core';
import { isEmpty } from 'lodash';
import React from 'react';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { LoadingComponent } from '../../../../components/core/LoadingComponent';
import { PermissionDenied } from '../../../../components/core/PermissionDenied';
import { AddIndividualGrievanceDetails } from '../../../../components/grievances/AddIndividualGrievanceDetails';
import { DeleteHouseholdGrievanceDetails } from '../../../../components/grievances/DeleteHouseholdGrievanceDetails';
import { DeleteIndividualGrievanceDetails } from '../../../../components/grievances/DeleteIndividualGrievanceDetails';
import { FlagDetails } from '../../../../components/grievances/FlagDetails';
import { GrievanceDetailsToolbar } from '../../../../components/grievances/GrievanceDetailsToolbar';
import { GrievancesApproveSection } from '../../../../components/grievances/GrievancesApproveSection/GrievancesApproveSection';
import { GrievancesDetails } from '../../../../components/grievances/GrievancesDetails/GrievancesDetails';
import { NeedsAdjudicationDetails } from '../../../../components/grievances/NeedsAdjudicationDetails';
import { Notes } from '../../../../components/grievances/Notes';
import { OtherRelatedTickets } from '../../../../components/grievances/OtherRelatedTickets';
import { PaymentIds } from '../../../../components/grievances/PaymentIds';
import { ReassignRoleBox } from '../../../../components/grievances/ReassignRoleBox';
import { RequestedHouseholdDataChange } from '../../../../components/grievances/RequestedHouseholdDataChange';
import { RequestedIndividualDataChange } from '../../../../components/grievances/RequestedIndividualDataChange';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { usePermissions } from '../../../../hooks/usePermissions';
import {
  GRIEVANCE_CATEGORIES,
  GRIEVANCE_ISSUE_TYPES,
  GRIEVANCE_TICKET_STATES,
} from '../../../../utils/constants';
import { isPermissionDeniedError } from '../../../../utils/utils';
import {
  useGrievancesChoiceDataQuery,
  useGrievanceTicketQuery,
  useMeQuery,
} from '../../../../__generated__/graphql';
import { grievancePermissions } from './grievancePermissions';

const PaddingContainer = styled.div`
  padding: 22px;
`;

export function GrievancesDetailsPage(): React.ReactElement {
  const { id } = useParams();
  const permissions = usePermissions();
  const {
    data: currentUserData,
    loading: currentUserDataLoading,
  } = useMeQuery();
  const { data, loading, error } = useGrievanceTicketQuery({
    variables: { id },
    fetchPolicy: 'network-only',
  });
  const ticket = data?.grievanceTicket;
  const currentUserId = currentUserData?.me?.id;
  const isCreator = currentUserId === ticket?.createdBy?.id;
  const isOwner = currentUserId === ticket?.assignedTo?.id;

  const businessArea = useBusinessArea();
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useGrievancesChoiceDataQuery();

  if (choicesLoading || loading || currentUserDataLoading)
    return <LoadingComponent />;
  if (isPermissionDeniedError(error)) return <PermissionDenied />;

  if (!data || !choicesData || !currentUserData || permissions === null)
    return null;

  const {
    canViewHouseholdDetails,
    canViewIndividualDetails,
    canEdit,
    canAddNote,
    canSetInProgress,
    canSetOnHold,
    canSendForApproval,
    canSendBack,
    canClose,
    canApproveDataChange,
    canApproveFlagAndAdjudication,
    canAssign,
  } = grievancePermissions(isCreator, isOwner, ticket, permissions);

  const shouldShowReassignBoxDataChange = (): boolean => {
    let { individual } = ticket;
    let { household } = ticket;
    if (ticket.category.toString() === GRIEVANCE_CATEGORIES.DEDUPLICATION) {
      individual = ticket.needsAdjudicationTicketDetails.selectedIndividual;
      household =
        ticket.needsAdjudicationTicketDetails.selectedIndividual?.household;
    }
    const isOneIndividual = household?.activeIndividualsCount === 1;

    if (isOneIndividual) return false;
    const isRightCategory =
      (ticket.category.toString() === GRIEVANCE_CATEGORIES.DATA_CHANGE &&
        ticket.issueType.toString() ===
          GRIEVANCE_ISSUE_TYPES.DELETE_INDIVIDUAL) ||
      (ticket.category.toString() === GRIEVANCE_CATEGORIES.DATA_CHANGE &&
        ticket.issueType.toString() ===
          GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL) ||
      (ticket.category.toString() === GRIEVANCE_CATEGORIES.SYSTEM_FLAGGING &&
        ticket?.systemFlaggingTicketDetails?.approveStatus) ||
      (ticket.category.toString() === GRIEVANCE_CATEGORIES.DEDUPLICATION &&
        ticket?.needsAdjudicationTicketDetails?.selectedIndividual);

    if (!isRightCategory) return false;

    const isRightStatus =
      ticket.status === GRIEVANCE_TICKET_STATES.FOR_APPROVAL;
    if (!isRightStatus) return false;

    const householdsAndRoles = individual?.householdsAndRoles;
    const isHeadOfHousehold = individual?.id === household?.headOfHousehold?.id;
    const hasRolesToReassign =
      householdsAndRoles?.filter((el) => el.role !== 'NO_ROLE').length > 0;

    let isProperDataChange = true;
    if (
      ticket.category.toString() === GRIEVANCE_CATEGORIES.DATA_CHANGE &&
      ticket.issueType.toString() === GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL
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

  const renderRightSection = (): React.ReactElement => {
    if (
      ticket.category.toString() === GRIEVANCE_CATEGORIES.PAYMENT_VERIFICATION
    )
      return (
        <Box display='flex' flexDirection='column'>
          <Box mt={6}>
            <PaymentIds
              verifications={
                ticket.paymentVerificationTicketDetails?.paymentVerifications
                  ?.edges
              }
            />
          </Box>
          <Box mt={6}>
            <OtherRelatedTickets
              ticket={ticket}
              linkedTickets={ticket.relatedTickets}
            />
          </Box>
        </Box>
      );
    if (shouldShowReassignBoxDataChange()) {
      return (
        <PaddingContainer>
          <Box display='flex' flexDirection='column'>
            <ReassignRoleBox
              shouldDisplayButton
              shouldDisableButton={
                ticket.deleteIndividualTicketDetails?.approveStatus
              }
              ticket={ticket}
            />
          </Box>
        </PaddingContainer>
      );
    }

    return (
      <PaddingContainer>
        <Box display='flex' flexDirection='column'>
          <OtherRelatedTickets
            ticket={ticket}
            linkedTickets={ticket.relatedTickets}
          />
        </Box>
      </PaddingContainer>
    );
  };

  return (
    <div>
      <GrievanceDetailsToolbar
        ticket={ticket}
        canEdit={canEdit}
        canSetInProgress={canSetInProgress}
        canSetOnHold={canSetOnHold}
        canSendForApproval={canSendForApproval}
        canSendBack={canSendBack}
        canClose={canClose}
        canAssign={canAssign}
      />
      <Grid container>
        <GrievancesDetails
          ticket={ticket}
          choicesData={choicesData}
          businessArea={businessArea}
          canViewHouseholdDetails={canViewHouseholdDetails}
          canViewIndividualDetails={canViewIndividualDetails}
        />
        <GrievancesApproveSection
          ticket={ticket}
          businessArea={businessArea}
          canApproveFlagAndAdjudication={canApproveFlagAndAdjudication}
          canApproveDataChange={canApproveDataChange}
        />
        <Grid item xs={9}>
          <PaddingContainer>
            <Notes notes={ticket.ticketNotes} canAddNote={canAddNote} />
          </PaddingContainer>
        </Grid>
        <Grid item xs={3}>
          {renderRightSection()}
        </Grid>
      </Grid>
    </div>
  );
}
