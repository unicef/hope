import {Box, Grid, Typography} from '@material-ui/core';
import React from 'react';
import {useParams} from 'react-router-dom';
import styled from 'styled-components';
import {useBusinessArea} from '../../hooks/useBusinessArea';
import {ContainerColumnWithBorder} from '../ContainerColumnWithBorder';
import {LabelizedField} from '../LabelizedField';
import {OverviewContainer} from '../OverviewContainer';
import {
  decodeIdString,
  grievanceTicketStatusToColor,
  isPermissionDeniedError,
  reduceChoices,
  renderUserName,
} from '../../utils/utils';
import {LoadingComponent} from '../LoadingComponent';
import {useGrievancesChoiceDataQuery, useGrievanceTicketQuery, useMeQuery,} from '../../__generated__/graphql';
import {GRIEVANCE_CATEGORIES, GRIEVANCE_ISSUE_TYPES, GRIEVANCE_TICKET_STATES,} from '../../utils/constants';
import {ContentLink} from '../ContentLink';
import {StatusBox} from '../StatusBox';
import {UniversalMoment} from '../UniversalMoment';
import {usePermissions} from '../../hooks/usePermissions';
import {hasCreatorOrOwnerPermissions, PERMISSIONS,} from '../../config/permissions';
import {PermissionDenied} from '../PermissionDenied';
import {Notes} from './Notes';
import {GrievanceDetailsToolbar} from './GrievanceDetailsToolbar';
import {PaymentIds} from './PaymentIds';
import {OtherRelatedTickets} from './OtherRelatedTickets';
import {AddIndividualGrievanceDetails} from './AddIndividualGrievanceDetails';
import {RequestedIndividualDataChange} from './RequestedIndividualDataChange';
import {RequestedHouseholdDataChange} from './RequestedHouseholdDataChange';
import {ReassignRoleBox} from './ReassignRoleBox';
import {DeleteIndividualGrievanceDetails} from './DeleteIndividualGrievanceDetails';
import {FlagDetails} from './FlagDetails';
import {NeedsAdjudicationDetails} from './NeedsAdjudicationDetails';

const PaddingContainer = styled.div`
  padding: 22px;
`;

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;

export function GrievanceDetailsPage(): React.ReactElement {
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

  const statusChoices: {
    [id: number]: string;
  } = reduceChoices(choicesData.grievanceTicketStatusChoices);

  const categoryChoices: {
    [id: number]: string;
  } = reduceChoices(choicesData.grievanceTicketCategoryChoices);

  const ticket = data.grievanceTicket;
  const currentUserId = currentUserData.me.id;
  const isCreator = currentUserId === ticket.createdBy?.id;
  const isOwner = currentUserId === ticket.assignedTo?.id;

  const canViewHouseholdDetails = hasCreatorOrOwnerPermissions(
    PERMISSIONS.GRIEVANCES_VIEW_HOUSEHOLD_DETAILS,
    isCreator,
    PERMISSIONS.GRIEVANCES_VIEW_HOUSEHOLD_DETAILS_AS_CREATOR,
    isOwner,
    PERMISSIONS.GRIEVANCES_VIEW_HOUSEHOLD_DETAILS_AS_OWNER,
    permissions,
  );

  const canViewIndividualDetails = hasCreatorOrOwnerPermissions(
    PERMISSIONS.GRIEVANCES_VIEW_INDIVIDUALS_DETAILS,
    isCreator,
    PERMISSIONS.GRIEVANCES_VIEW_INDIVIDUALS_DETAILS_AS_CREATOR,
    isOwner,
    PERMISSIONS.GRIEVANCES_VIEW_INDIVIDUALS_DETAILS_AS_OWNER,
    permissions,
  );

  const canEdit = hasCreatorOrOwnerPermissions(
    PERMISSIONS.GRIEVANCES_UPDATE,
    isCreator,
    PERMISSIONS.GRIEVANCES_UPDATE_AS_CREATOR,
    isOwner,
    PERMISSIONS.GRIEVANCES_UPDATE_AS_OWNER,
    permissions,
  );

  const canAddNote = hasCreatorOrOwnerPermissions(
    PERMISSIONS.GRIEVANCES_ADD_NOTE,
    isCreator,
    PERMISSIONS.GRIEVANCES_ADD_NOTE_AS_CREATOR,
    isOwner,
    PERMISSIONS.GRIEVANCES_ADD_NOTE_AS_OWNER,
    permissions,
  );

  const canSetInProgress = hasCreatorOrOwnerPermissions(
    PERMISSIONS.GRIEVANCES_SET_IN_PROGRESS,
    isCreator,
    PERMISSIONS.GRIEVANCES_SET_IN_PROGRESS_AS_CREATOR,
    isOwner,
    PERMISSIONS.GRIEVANCES_SET_IN_PROGRESS_AS_OWNER,
    permissions,
  );

  const canSetOnHold = hasCreatorOrOwnerPermissions(
    PERMISSIONS.GRIEVANCES_SET_ON_HOLD,
    isCreator,
    PERMISSIONS.GRIEVANCES_SET_ON_HOLD_AS_CREATOR,
    isOwner,
    PERMISSIONS.GRIEVANCES_SET_ON_HOLD_AS_OWNER,
    permissions,
  );

  const canSendForApproval = hasCreatorOrOwnerPermissions(
    PERMISSIONS.GRIEVANCES_SEND_FOR_APPROVAL,
    isCreator,
    PERMISSIONS.GRIEVANCES_SEND_FOR_APPROVAL_AS_CREATOR,
    isOwner,
    PERMISSIONS.GRIEVANCES_SEND_FOR_APPROVAL_AS_OWNER,
    permissions,
  );
  const canSendBack = hasCreatorOrOwnerPermissions(
    PERMISSIONS.GRIEVANCES_SEND_BACK,
    isCreator,
    PERMISSIONS.GRIEVANCES_SEND_BACK_AS_CREATOR,
    isOwner,
    PERMISSIONS.GRIEVANCES_SEND_BACK_AS_OWNER,
    permissions,
  );
  const isFeedbackType = [
    GRIEVANCE_CATEGORIES.POSITIVE_FEEDBACK,
    GRIEVANCE_CATEGORIES.NEGATIVE_FEEDBACK,
    GRIEVANCE_CATEGORIES.REFERRAL,
  ].includes(ticket.category.toString());
  const canClose =
    (isFeedbackType &&
      hasCreatorOrOwnerPermissions(
        PERMISSIONS.GRIEVANCES_CLOSE_TICKET_FEEDBACK,
        isCreator,
        PERMISSIONS.GRIEVANCES_CLOSE_TICKET_FEEDBACK_AS_CREATOR,
        isOwner,
        PERMISSIONS.GRIEVANCES_CLOSE_TICKET_FEEDBACK_AS_OWNER,
        permissions,
      )) ||
    (!isFeedbackType &&
      hasCreatorOrOwnerPermissions(
        PERMISSIONS.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
        isCreator,
        PERMISSIONS.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_CREATOR,
        isOwner,
        PERMISSIONS.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_OWNER,
        permissions,
      ));

  const canApproveDataChange = hasCreatorOrOwnerPermissions(
    PERMISSIONS.GRIEVANCES_APPROVE_DATA_CHANGE,
    isCreator,
    PERMISSIONS.GRIEVANCES_APPROVE_DATA_CHANGE_AS_CREATOR,
    isOwner,
    PERMISSIONS.GRIEVANCES_APPROVE_DATA_CHANGE_AS_OWNER,
    permissions,
  );

  const canApproveFlagAndAdjudication = hasCreatorOrOwnerPermissions(
    PERMISSIONS.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
    isCreator,
    PERMISSIONS.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_CREATOR,
    isOwner,
    PERMISSIONS.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_OWNER,
    permissions,
  );

  const issueType = ticket.issueType
    ? choicesData.grievanceTicketIssueTypeChoices
        .filter((el) => el.category === ticket.category.toString())[0]
        .subCategories.filter(
          (el) => el.value === ticket.issueType.toString(),
        )[0].name
    : '-';

  const FieldsArray: {
    label: string;
    value: React.ReactElement;
    size: boolean | 3 | 6 | 8 | 11 | 'auto' | 1 | 2 | 4 | 5 | 7 | 9 | 10 | 12;
  }[] = [
    {
      label: 'STATUS',
      value: (
        <StatusContainer>
          <StatusBox
            status={statusChoices[ticket.status]}
            statusToColor={grievanceTicketStatusToColor}
          />
        </StatusContainer>
      ),
      size: 3,
    },
    {
      label: 'CATEGORY',
      value: <span>{categoryChoices[ticket.category]}</span>,
      size: 3,
    },
    {
      label: 'Issue Type',
      value: <span>{issueType}</span>,
      size: 6,
    },
    {
      label: 'HOUSEHOLD ID',
      value: (
        <span>
          {ticket.household?.id ? (
            <ContentLink
              href={
                canViewHouseholdDetails
                  ? `/${businessArea}/population/household/${ticket.household.id}`
                  : undefined
              }
            >
              {ticket.household.unicefId}
            </ContentLink>
          ) : (
            '-'
          )}
        </span>
      ),
      size: 3,
    },
    {
      label: 'INDIVIDUAL ID',
      value: (
        <span>
          {ticket.individual?.id ? (
            <ContentLink
              href={
                canViewIndividualDetails
                  ? `/${businessArea}/population/individuals/${ticket.individual.id}`
                  : undefined
              }
            >
              {ticket.individual.unicefId}
            </ContentLink>
          ) : (
            '-'
          )}
        </span>
      ),
      size: 3,
    },
    {
      label: 'PAYMENT ID',
      value: (
        <span>
          {ticket.paymentRecord?.id ? (
            <ContentLink
              href={`/${businessArea}/payment-records/${ticket.paymentRecord.id}`}
            >
              {decodeIdString(ticket.paymentRecord.id)}
            </ContentLink>
          ) : (
            '-'
          )}
        </span>
      ),
      size: 6,
    },
    {
      label: 'CONSENT',
      value: <span>{ticket.consent ? 'Yes' : 'No'}</span>,
      size: 3,
    },
    {
      label: 'CREATED BY',
      value: <span>{renderUserName(ticket.createdBy)}</span>,
      size: 3,
    },
    {
      label: 'DATE CREATED',
      value: <UniversalMoment>{ticket.createdAt}</UniversalMoment>,
      size: 3,
    },
    {
      label: 'LAST MODIFIED DATE',
      value: <UniversalMoment>{ticket.updatedAt}</UniversalMoment>,
      size: 3,
    },
    {
      label: 'DESCRIPTION',
      value: <span>{ticket.description || '-'}</span>,
      size: 6,
    },
    {
      label: 'ASSIGNED TO',
      value: <span>{renderUserName(ticket.assignedTo) || '-'}</span>,
      size: 6,
    },
    {
      label: 'ADMINISTRATIVE LEVEL 2',
      value: <span>{ticket.admin}</span>,
      size: 3,
    },
    {
      label: 'AREA / VILLAGE / PAY POINT',
      value: <span>{ticket.area}</span>,
      size: 3,
    },
    {
      label: 'LANGUAGES SPOKEN',
      value: <span>{ticket.language || '-'}</span>,
      size: 3,
    },
  ];
  const shouldShowReassignBoxDataChange = (): boolean => {
    let { individual } = ticket;
    let { household } = ticket;
    if (ticket.category.toString() === GRIEVANCE_CATEGORIES.DEDUPLICATION) {
      individual = ticket.needsAdjudicationTicketDetails.selectedIndividual;
      household =
        ticket.needsAdjudicationTicketDetails.selectedIndividual?.household;
    }

    const householdsAndRoles = individual?.householdsAndRoles;
    const isHeadOfHousehold = individual?.id === household?.headOfHousehold?.id;
    const hasRolesToReassign =
      householdsAndRoles?.filter((el) => el.role !== 'NO_ROLE').length > 0;

    const isRightCategory =
      (ticket.category.toString() === GRIEVANCE_CATEGORIES.DATA_CHANGE &&
        ticket.issueType.toString() ===
          GRIEVANCE_ISSUE_TYPES.DELETE_INDIVIDUAL) ||
      (ticket.category.toString() === GRIEVANCE_CATEGORIES.SYSTEM_FLAGGING &&
        ticket?.systemFlaggingTicketDetails?.approveStatus) ||
      (ticket.category.toString() === GRIEVANCE_CATEGORIES.DEDUPLICATION &&
        ticket?.needsAdjudicationTicketDetails?.selectedIndividual);
    const isRightStatus =
      ticket.status === GRIEVANCE_TICKET_STATES.FOR_APPROVAL;
    return (
      isRightCategory &&
      isRightStatus &&
      (isHeadOfHousehold || hasRolesToReassign)
    );
  };

  // const shouldShowReassignBoxFlag = (): boolean => {
  //   //add condition here
  //   return true;
  // };

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
    // if (shouldShowReassignBoxFlag())
    //   return (
    //     <PaddingContainer>
    //       <Box display='flex' flexDirection='column'>
    //         <ReassignRoleBox shouldDisplayButton={false} ticket={ticket} />
    //       </Box>
    //     </PaddingContainer>
    //   );
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
      />
      <Grid container>
        <Grid item xs={12}>
          <ContainerColumnWithBorder>
            <Title>
              <Typography variant='h6'>Details</Typography>
            </Title>
            <OverviewContainer>
              <Grid container spacing={6}>
                {FieldsArray.map((el) => (
                  <Grid key={el.label} item xs={el.size}>
                    <LabelizedField label={el.label}>{el.value}</LabelizedField>
                  </Grid>
                ))}
              </Grid>
            </OverviewContainer>
          </ContainerColumnWithBorder>
        </Grid>
        <Grid item xs={7}>
          {ticket?.category?.toString() ===
            GRIEVANCE_CATEGORIES.SYSTEM_FLAGGING && (
            <PaddingContainer>
              <FlagDetails
                ticket={ticket}
                canApproveFlag={canApproveFlagAndAdjudication}
              />
            </PaddingContainer>
          )}
          {ticket?.category?.toString() ===
            GRIEVANCE_CATEGORIES.DEDUPLICATION && (
            <PaddingContainer>
              <NeedsAdjudicationDetails
                ticket={ticket}
                canApprove={canApproveFlagAndAdjudication}
              />
            </PaddingContainer>
          )}
          {ticket?.issueType?.toString() ===
            GRIEVANCE_ISSUE_TYPES.ADD_INDIVIDUAL && (
            <PaddingContainer>
              <AddIndividualGrievanceDetails
                ticket={ticket}
                canApproveDataChange={canApproveDataChange}
              />
            </PaddingContainer>
          )}
          {ticket?.issueType?.toString() ===
            GRIEVANCE_ISSUE_TYPES.DELETE_INDIVIDUAL && (
            <PaddingContainer>
              <DeleteIndividualGrievanceDetails
                ticket={ticket}
                canApproveDataChange={canApproveDataChange}
              />
            </PaddingContainer>
          )}
          {ticket?.issueType?.toString() ===
            GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL && (
            <PaddingContainer>
              <RequestedIndividualDataChange
                ticket={ticket}
                canApproveDataChange={canApproveDataChange}
              />
            </PaddingContainer>
          )}
          {ticket?.issueType?.toString() ===
            GRIEVANCE_ISSUE_TYPES.EDIT_HOUSEHOLD && (
            <PaddingContainer>
              <RequestedHouseholdDataChange
                ticket={ticket}
                canApproveDataChange={canApproveDataChange}
              />
            </PaddingContainer>
          )}
          <PaddingContainer>
            <Notes notes={ticket.ticketNotes} canAddNote={canAddNote} />
          </PaddingContainer>
        </Grid>
        <Grid item xs={5}>
          {renderRightSection()}
        </Grid>
      </Grid>
    </div>
  );
}
