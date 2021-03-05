import { Box, Button } from '@material-ui/core';
import { useParams, Link } from 'react-router-dom';
import EditIcon from '@material-ui/icons/EditRounded';
import React from 'react';
import styled from 'styled-components';
import { MiśTheme } from '../../theme';
import { BreadCrumbsItem } from '../BreadCrumbs';
import {
  GRIEVANCE_CATEGORIES,
  GRIEVANCE_TICKET_STATES,
} from '../../utils/constants';
import { decodeIdString } from '../../utils/utils';
import {
  GrievanceTicketDocument,
  GrievanceTicketQuery,
  useGrievanceTicketStatusChangeMutation,
} from '../../__generated__/graphql';
import { PageHeader } from '../PageHeader';
import { ConfirmationDialog } from '../ConfirmationDialog';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { ButtonDialog } from '../ButtonDialog';

const Separator = styled.div`
  width: 1px;
  height: 28px;
  border: 1px solid
    ${({ theme }: { theme: MiśTheme }) => theme.hctPalette.lightGray};
  margin: 0 28px;
`;

export const GrievanceDetailsToolbar = ({
  ticket,
  canEdit,
  canSetInProgress,
  canSetOnHold,
  canSendForApproval,
  canSendBack,
  canClose,
}: {
  ticket: GrievanceTicketQuery['grievanceTicket'];
  canEdit: boolean;
  canSetInProgress: boolean;
  canSetOnHold: boolean;
  canSendForApproval: boolean;
  canSendBack: boolean;
  canClose: boolean;
}): React.ReactElement => {
  const { id } = useParams();
  const businessArea = useBusinessArea();
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Grievance and Feedback',
      to: `/${businessArea}/grievance-and-feedback/`,
    },
  ];
  const [mutate] = useGrievanceTicketStatusChangeMutation();

  const isNew = ticket.status === GRIEVANCE_TICKET_STATES.NEW;
  const isAssigned = ticket.status === GRIEVANCE_TICKET_STATES.ASSIGNED;
  const isInProgress = ticket.status === GRIEVANCE_TICKET_STATES.IN_PROGRESS;
  const isForApproval = ticket.status === GRIEVANCE_TICKET_STATES.FOR_APPROVAL;
  const isOnHold = ticket.status === GRIEVANCE_TICKET_STATES.ON_HOLD;
  const isClosed = ticket.status === GRIEVANCE_TICKET_STATES.CLOSED;
  const isEditable = !isClosed;

  const isFeedbackType =
    ticket.category.toString() === GRIEVANCE_CATEGORIES.POSITIVE_FEEDBACK ||
    ticket.category.toString() === GRIEVANCE_CATEGORIES.NEGATIVE_FEEDBACK ||
    ticket.category.toString() === GRIEVANCE_CATEGORIES.REFERRAL;

  const getClosingConfirmationExtraText = (): string => {
    if (ticket.category.toString() !== GRIEVANCE_CATEGORIES.DATA_CHANGE) {
      return '';
    }
    let approved = 0;
    let notApproved = 0;

    const countApproved = (data): void => {
      if (!Array.isArray(data)) return;
      for (const value of data) {
        if (value && !Array.isArray(value) && value.value) {
          if (value.approve_status === true) {
            approved += 1;
          } else if (value.approve_status === false) {
            notApproved += 1;
          }
        }
      }
    };
    const arrayToCount = [];

    arrayToCount.push(
      Object.values(
        ticket.householdDataUpdateTicketDetails?.householdData || {},
      ),
    );
    arrayToCount.push(
      Object.values(
        ticket.householdDataUpdateTicketDetails?.householdData.flex_fields ||
          {},
      ),
    );
    arrayToCount.push(
      Object.values(
        ticket.individualDataUpdateTicketDetails?.individualData || {},
      ),
    );
    arrayToCount.push(
      Object.values(
        ticket.individualDataUpdateTicketDetails?.individualData.flex_fields ||
          {},
      ),
    );
    arrayToCount.push(
      ticket.individualDataUpdateTicketDetails?.individualData.documents || [],
    );
    arrayToCount.push(
      ticket.individualDataUpdateTicketDetails?.individualData
        .documents_to_remove || [],
    );

    arrayToCount.forEach((value) => countApproved(value));

    // all changes were approved
    if (!notApproved) return '';

    // no changes were approved
    if (!approved)
      return `You did not approved any changes. All change requests (${notApproved}) will be automatically rejected.`;

    // some changes were approved
    return `You approved ${approved} change${
      approved > 1 ? 's' : ''
    }. Remaining change requests (${notApproved}) will be automatically rejected.`;
  };

  const closingConfirmationText = 'Are you sure you want to close the ticket?';

  const changeState = (status): void => {
    mutate({
      variables: {
        grievanceTicketId: ticket.id,
        status,
      },
      refetchQueries: () => [
        {
          query: GrievanceTicketDocument,
          variables: { id: ticket.id },
        },
      ],
    });
  };
  let closeButton = (
    <ConfirmationDialog
      title='Close ticket'
      extraContent={getClosingConfirmationExtraText()}
      content={closingConfirmationText}
      continueText='close ticket'
    >
      {(confirm) => (
        <Button
          color='primary'
          variant='contained'
          onClick={confirm(() => changeState(GRIEVANCE_TICKET_STATES.CLOSED))}
        >
          Close Ticket
        </Button>
      )}
    </ConfirmationDialog>
  );
  if (
    ticket.category.toString() === GRIEVANCE_CATEGORIES.DEDUPLICATION &&
    ticket?.needsAdjudicationTicketDetails?.hasDuplicatedDocument &&
    !ticket?.needsAdjudicationTicketDetails?.selectedIndividual
  ) {
    closeButton = (
      <ButtonDialog
        title='Duplicate Document Conflict'
        buttonText='Close Ticket'
        message='The individuals have matching document numbers. HOPE requires that document numbers are unique. Please resolve before closing the ticket.'
      />
    );
  }
  return (
    <PageHeader
      title={`Ticket #${decodeIdString(id)}`}
      breadCrumbs={breadCrumbsItems}
    >
      <Box display='flex' alignItems='center'>
        {isEditable && canEdit && (
          <>
            <Button
              color='primary'
              variant='outlined'
              component={Link}
              to={`/${businessArea}/grievance-and-feedback/edit-ticket/${id}`}
              startIcon={<EditIcon />}
            >
              Edit
            </Button>
            <Separator />
          </>
        )}
        {isNew && canEdit && (
          <>
            <Button
              color='primary'
              variant='contained'
              onClick={() => changeState(GRIEVANCE_TICKET_STATES.ASSIGNED)}
            >
              ASSIGN TO ME
            </Button>
          </>
        )}
        {isAssigned && canSetInProgress && (
          <Button
            color='primary'
            variant='contained'
            onClick={() => changeState(GRIEVANCE_TICKET_STATES.IN_PROGRESS)}
          >
            Set to in progress
          </Button>
        )}
        {isInProgress && (
          <>
            {canSetOnHold && (
              <Box mr={3}>
                <Button
                  color='primary'
                  variant='outlined'
                  onClick={() => changeState(GRIEVANCE_TICKET_STATES.ON_HOLD)}
                >
                  Set On Hold
                </Button>
              </Box>
            )}
            {canSendForApproval && (
              <Box mr={3}>
                <Button
                  color='primary'
                  variant='contained'
                  onClick={() =>
                    changeState(GRIEVANCE_TICKET_STATES.FOR_APPROVAL)
                  }
                >
                  Send For Approval
                </Button>
              </Box>
            )}
            {isFeedbackType && canClose && (
              <ConfirmationDialog
                title='Confirmation'
                content={closingConfirmationText}
                continueText='close ticket'
              >
                {(confirm) => (
                  <Button
                    color='primary'
                    variant='contained'
                    onClick={confirm(() =>
                      changeState(GRIEVANCE_TICKET_STATES.CLOSED),
                    )}
                  >
                    Close Ticket
                  </Button>
                )}
              </ConfirmationDialog>
            )}
          </>
        )}
        {isOnHold && (
          <>
            {canSetInProgress && (
              <Box mr={3}>
                <Button
                  color='primary'
                  variant='contained'
                  onClick={() =>
                    changeState(GRIEVANCE_TICKET_STATES.IN_PROGRESS)
                  }
                >
                  Set to in progress
                </Button>
              </Box>
            )}
            {canSendForApproval && (
              <Box mr={3}>
                <Button
                  color='primary'
                  variant='contained'
                  onClick={() =>
                    changeState(GRIEVANCE_TICKET_STATES.FOR_APPROVAL)
                  }
                >
                  Send For Approval
                </Button>
              </Box>
            )}
            {isFeedbackType && canClose && (
              <ConfirmationDialog
                title='Confirmation'
                content={closingConfirmationText}
                continueText='close ticket'
              >
                {(confirm) => (
                  <Button
                    color='primary'
                    variant='contained'
                    onClick={confirm(() =>
                      changeState(GRIEVANCE_TICKET_STATES.CLOSED),
                    )}
                  >
                    Close Ticket
                  </Button>
                )}
              </ConfirmationDialog>
            )}
          </>
        )}
        {isForApproval && (
          <>
            {canSendBack && (
              <Box mr={3}>
                <Button
                  color='primary'
                  variant='contained'
                  onClick={() =>
                    changeState(GRIEVANCE_TICKET_STATES.IN_PROGRESS)
                  }
                >
                  Send Back
                </Button>
              </Box>
            )}
            {canClose && closeButton}
          </>
        )}
      </Box>
    </PageHeader>
  );
};
