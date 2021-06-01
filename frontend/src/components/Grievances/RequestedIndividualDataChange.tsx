import { Box, Button, Paper, Typography } from '@material-ui/core';
import styled from 'styled-components';
import React, { ReactElement, useState } from 'react';
import { Formik } from 'formik';
import mapKeys from 'lodash/mapKeys';
import camelCase from 'lodash/camelCase';
import { ConfirmationDialog } from '../ConfirmationDialog';
import { useSnackbar } from '../../hooks/useSnackBar';
import {
  GrievanceTicketQuery,
  useApproveIndividualDataChangeMutation,
} from '../../__generated__/graphql';
import { GRIEVANCE_TICKET_STATES } from '../../utils/constants';
import { RequestedIndividualDataChangeTable } from './RequestedIndividualDataChangeTable';

const StyledBox = styled(Paper)`
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 26px 22px;
`;

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

export function RequestedIndividualDataChange({
  ticket,
  canApproveDataChange,
}: {
  ticket: GrievanceTicketQuery['grievanceTicket'];
  canApproveDataChange: boolean;
}): React.ReactElement {
  const { showMessage } = useSnackbar();
  const individualData = {
    ...ticket.individualDataUpdateTicketDetails.individualData,
  };
  let allApprovedCount = 0;
  const documents = individualData?.documents || [];
  const documentsToRemove = individualData.documents_to_remove || [];
  const identities = individualData?.identities || [];
  const identitiesToRemove = individualData.identities_to_remove || [];
  const flexFields = individualData.flex_fields || {};
  delete individualData.flex_fields;
  delete individualData.documents;
  delete individualData.identities;
  delete individualData.documents_to_remove;
  delete individualData.identities_to_remove;
  delete individualData.previous_documents;
  delete individualData.previous_identities;

  const entries = Object.entries(individualData);
  const entriesFlexFields = Object.entries(flexFields);
  allApprovedCount += documents.filter((el) => el.approve_status).length;
  allApprovedCount += documentsToRemove.filter((el) => el.approve_status)
    .length;
  allApprovedCount += identities.filter((el) => el.approve_status).length;
  allApprovedCount += identitiesToRemove.filter((el) => el.approve_status)
    .length;
  allApprovedCount += entries.filter(
    ([, value]: [string, { approve_status: boolean }]) => value.approve_status,
  ).length;
  allApprovedCount += entriesFlexFields.filter(
    ([, value]: [string, { approve_status: boolean }]) => value.approve_status,
  ).length;

  const [isEdit, setEdit] = useState(allApprovedCount === 0);
  const getConfirmationText = (allChangesLength): string => {
    return `You approved ${allChangesLength || 0} change${
      allChangesLength === 1 ? '' : 's'
    }, remaining proposed changes will be automatically rejected upon ticket closure.`;
  };
  const [mutate] = useApproveIndividualDataChangeMutation();
  const selectedDocuments = [];
  const selectedDocumentsToRemove = [];
  // eslint-disable-next-line no-plusplus
  for (let i = 0; i < documents?.length; i++) {
    if (documents[i]?.approve_status) {
      selectedDocuments.push(i);
    }
  }
  // eslint-disable-next-line no-plusplus
  for (let i = 0; i < documentsToRemove?.length; i++) {
    if (documentsToRemove[i]?.approve_status) {
      selectedDocumentsToRemove.push(i);
    }
  }
  const selectedIdentities = [];
  const selectedIdentitiesToRemove = [];
  // eslint-disable-next-line no-plusplus
  for (let i = 0; i < identities?.length; i++) {
    if (identities[i]?.approve_status) {
      selectedIdentities.push(i);
    }
  }
  // eslint-disable-next-line no-plusplus
  for (let i = 0; i < identitiesToRemove?.length; i++) {
    if (identitiesToRemove[i]?.approve_status) {
      selectedIdentitiesToRemove.push(i);
    }
  }
  const shouldShowEditButton = (allChangesLength): boolean =>
    allChangesLength &&
    !isEdit &&
    ticket.status === GRIEVANCE_TICKET_STATES.FOR_APPROVAL;

  const areAllApproved = (allSelected): boolean => {
    const countAll =
      entries.length +
      entriesFlexFields.length +
      documents.length +
      documentsToRemove.length +
      identities.length +
      identitiesToRemove.length;
    return allSelected === countAll;
  };

  const getApprovalButton = (allSelected, submitForm): ReactElement => {
    if (areAllApproved(allSelected)) {
      return (
        <Button
          onClick={submitForm}
          variant='contained'
          color='primary'
          disabled={ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL}
        >
          Approve
        </Button>
      );
    }
    return (
      <ConfirmationDialog
        title='Warning'
        content={getConfirmationText(allSelected)}
      >
        {(confirm) => (
          <Button
            onClick={confirm(() => submitForm())}
            variant='contained'
            color='primary'
            disabled={ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL}
          >
            Approve
          </Button>
        )}
      </ConfirmationDialog>
    );
  };

  return (
    <Formik
      initialValues={{
        selected: entries
          .filter((row) => {
            const valueDetails = mapKeys(row[1], (v, k) => camelCase(k)) as {
              value: string;
              approveStatus: boolean;
            };
            return valueDetails.approveStatus;
          })
          .map((row) => camelCase(row[0])),
        selectedFlexFields: entriesFlexFields
          .filter((row) => {
            const valueDetails = mapKeys(row[1], (v, k) => camelCase(k)) as {
              value: string;
              approveStatus: boolean;
            };
            return valueDetails.approveStatus;
          })
          .map((row) => row[0]),
        selectedDocuments,
        selectedDocumentsToRemove,
        selectedIdentities,
        selectedIdentitiesToRemove,
      }}
      onSubmit={async (values) => {
        const individualApproveData = values.selected.reduce((prev, curr) => {
          // eslint-disable-next-line no-param-reassign
          prev[curr] = true;
          return prev;
        }, {});
        const approvedDocumentsToCreate = values.selectedDocuments;
        const approvedDocumentsToRemove = values.selectedDocumentsToRemove;
        const approvedIdentitiesToCreate = values.selectedIdentities;
        const approvedIdentitiesToRemove = values.selectedIdentitiesToRemove;
        const flexFieldsApproveData = values.selectedFlexFields.reduce(
          (prev, curr) => {
            // eslint-disable-next-line no-param-reassign
            prev[curr] = true;
            return prev;
          },
          {},
        );
        try {
          await mutate({
            variables: {
              grievanceTicketId: ticket.id,
              individualApproveData: JSON.stringify(individualApproveData),
              approvedDocumentsToCreate,
              approvedDocumentsToRemove,
              approvedIdentitiesToCreate,
              approvedIdentitiesToRemove,
              flexFieldsApproveData: JSON.stringify(flexFieldsApproveData),
            },
          });
          showMessage('Changes Approved');
          const sum =
            values.selected.length +
            values.selectedFlexFields.length +
            values.selectedDocuments.length +
            values.selectedDocumentsToRemove.length +
            values.selectedIdentities.length +
            values.selectedIdentitiesToRemove.length;
          setEdit(sum === 0);
        } catch (e) {
          e.graphQLErrors.map((x) => showMessage(x.message));
        }
      }}
    >
      {({ submitForm, setFieldValue, values }) => {
        const allChangesLength =
          values.selected.length +
          values.selectedFlexFields.length +
          values.selectedDocuments.length +
          values.selectedDocumentsToRemove.length +
          values.selectedIdentities.length +
          values.selectedIdentitiesToRemove.length;

        return (
          <StyledBox>
            <Title>
              <Box display='flex' justifyContent='space-between'>
                <Typography variant='h6'>Requested Data Change</Typography>
                {shouldShowEditButton(allChangesLength) ? (
                  <Button
                    onClick={() => setEdit(true)}
                    variant='outlined'
                    color='primary'
                    disabled={ticket.status === GRIEVANCE_TICKET_STATES.CLOSED}
                  >
                    EDIT
                  </Button>
                ) : (
                  canApproveDataChange &&
                  getApprovalButton(allChangesLength, submitForm)
                )}
              </Box>
            </Title>
            <RequestedIndividualDataChangeTable
              values={values}
              ticket={ticket}
              setFieldValue={setFieldValue}
              isEdit={isEdit}
            />
          </StyledBox>
        );
      }}
    </Formik>
  );
}
