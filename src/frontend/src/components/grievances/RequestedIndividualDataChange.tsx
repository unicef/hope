/* eslint-disable react-hooks/rules-of-hooks */

import { Box, Button, Paper, Typography } from '@mui/material';
import { Formik } from 'formik';
import camelCase from 'lodash/camelCase';
import mapKeys from 'lodash/mapKeys';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useSnackbar } from '@hooks/useSnackBar';
import {
  GRIEVANCE_ISSUE_TYPES,
  GRIEVANCE_TICKET_STATES,
} from '@utils/constants';
import {
  GrievanceTicketQuery,
  HouseholdNode,
  IndividualNode,
  IndividualRoleInHouseholdRole,
  useApproveIndividualDataChangeMutation,
} from '@generated/graphql';
import { useConfirmation } from '@core/ConfirmationDialog';
import { Title } from '@core/Title';
import { RequestedIndividualDataChangeTable } from './RequestedIndividualDataChangeTable/RequestedIndividualDataChangeTable';

const StyledBox = styled(Paper)`
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 26px 22px;
`;

export type RoleReassignData = {
  role: IndividualRoleInHouseholdRole | string;
  individual: IndividualNode;
  household: HouseholdNode;
};

export function RequestedIndividualDataChange({
  ticket,
  canApproveDataChange,
}: {
  ticket: GrievanceTicketQuery['grievanceTicket'];
  canApproveDataChange: boolean;
}): ReactElement {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const confirm = useConfirmation();
  const individualData = {
    ...ticket.individualDataUpdateTicketDetails.individualData,
  };
  let allApprovedCount = 0;
  const isForApproval = ticket.status === GRIEVANCE_TICKET_STATES.FOR_APPROVAL;
  const documents = individualData?.documents || [];
  const documentsToRemove = individualData.documents_to_remove || [];
  const documentsToEdit = individualData.documents_to_edit || [];
  const identities = individualData?.identities || [];
  const identitiesToRemove = individualData.identities_to_remove || [];
  const identitiesToEdit = individualData.identities_to_edit || [];
  const accounts = individualData.accounts || [];
  const accountsToEdit = individualData.accounts_to_edit || [];
  const flexFields = individualData.flex_fields || {};

  delete individualData.flex_fields;
  delete individualData.documents;
  delete individualData.documents_to_edit;
  delete individualData.documents_to_remove;
  delete individualData.previous_documents;

  delete individualData.identities;
  delete individualData.identities_to_edit;
  delete individualData.identities_to_remove;
  delete individualData.previous_identities;

  delete individualData.accounts;
  delete individualData.accounts_to_edit;


  const entries = Object.entries(individualData);
  const entriesFlexFields = Object.entries(flexFields);
  allApprovedCount += documents.filter((el) => el.approve_status).length;
  allApprovedCount += documentsToRemove.filter(
    (el) => el.approve_status,
  ).length;
  allApprovedCount += documentsToEdit.filter((el) => el.approve_status).length;
  allApprovedCount += identities.filter((el) => el.approve_status).length;
  allApprovedCount += identitiesToRemove.filter(
    (el) => el.approve_status,
  ).length;
  allApprovedCount += identitiesToEdit.filter((el) => el.approve_status).length;
  allApprovedCount += entries.filter(
    ([, value]: [string, { approve_status: boolean }]) => value.approve_status,
  ).length;
  allApprovedCount += accounts.filter((el) => el.approve_status).length;
  allApprovedCount += accountsToEdit.filter(
    (el) => el.approve_status,
  ).length;
  allApprovedCount += entriesFlexFields.filter(
    ([, value]: [string, { approve_status: boolean }]) => value.approve_status,
  ).length;

  const [isEdit, setEdit] = useState(allApprovedCount === 0);
  const getConfirmationText = (allChangesLength): string =>
    `You approved ${allChangesLength || 0} change${
      allChangesLength === 1 ? '' : 's'
    }, remaining proposed changes will be automatically rejected upon ticket closure.`;
  const [mutate] = useApproveIndividualDataChangeMutation();
  const selectedDocuments = [];
  const selectedDocumentsToRemove = [];
  const selectedDocumentsToEdit = [];
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
  // eslint-disable-next-line no-plusplus
  for (let i = 0; i < documentsToEdit?.length; i++) {
    if (documentsToEdit[i]?.approve_status) {
      selectedDocumentsToEdit.push(i);
    }
  }
  const selectedIdentities = [];
  const selectedIdentitiesToRemove = [];
  const selectedIdentitiesToEdit = [];
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
  // eslint-disable-next-line no-plusplus
  for (let i = 0; i < identitiesToEdit?.length; i++) {
    if (identitiesToEdit[i]?.approve_status) {
      selectedIdentitiesToEdit.push(i);
    }
  }

  const selectedAccounts = [];
  // eslint-disable-next-line no-plusplus
  for (let i = 0; i < accounts?.length; i++) {
    if (accounts[i]?.approve_status) {
      selectedAccounts.push(i);
    }
  }
  const selectedAccountsToEdit = [];
  // eslint-disable-next-line no-plusplus
  for (let i = 0; i < accountsToEdit?.length; i++) {
    if (accountsToEdit[i]?.approve_status) {
      selectedAccountsToEdit.push(i);
    }
  }

  const isHeadOfHousehold =
    ticket.individual?.id === ticket.household?.headOfHousehold?.id;

  const primaryCollectorRolesCount =
    ticket?.individual?.householdsAndRoles.filter(
      (el) => el.role === IndividualRoleInHouseholdRole.Primary,
    ).length + (isHeadOfHousehold ? 1 : 0);
  const primaryColletorRolesReassignedCount = Object.values(
    JSON.parse(ticket.individualDataUpdateTicketDetails.roleReassignData),
  )?.filter(
    (el: RoleReassignData) =>
      el.role === IndividualRoleInHouseholdRole.Primary || el.role === 'HEAD',
  ).length;

  let approveEnabled = false;
  if (ticket.issueType.toString() === GRIEVANCE_ISSUE_TYPES.DELETE_INDIVIDUAL) {
    approveEnabled =
      isForApproval &&
      primaryCollectorRolesCount === primaryColletorRolesReassignedCount;
  } else {
    approveEnabled = isForApproval;
  }

  const shouldShowEditButton = (allChangesLength): boolean =>
    allChangesLength && !isEdit && isForApproval;

  const areAllApproved = (allSelected): boolean => {
    const countAll =
      entries.length +
      entriesFlexFields.length +
      documents.length +
      documentsToRemove.length +
      documentsToEdit.length +
      identities.length +
      identitiesToRemove.length +
      accounts.length +
      accountsToEdit.length +
      identitiesToEdit.length;

    return allSelected === countAll;
  };

  const getApprovalButton = (allSelected, submitForm): ReactElement => {
    if (areAllApproved(allSelected)) {
      return (
        <Button
          onClick={submitForm}
          variant="contained"
          color="primary"
          disabled={!approveEnabled}
          data-cy="button-approve"
        >
          {t('Approve')}
        </Button>
      );
    }
    return (
      <Button
        onClick={() =>
          confirm({
            title: t('Warning'),
            content: getConfirmationText(allSelected),
          }).then(() => {
            submitForm();
          })
        }
        variant="contained"
        color="primary"
        disabled={!approveEnabled}
        data-cy="button-approve"
      >
        {t('Approve')}
      </Button>
    );
  };

  return (
    <Formik
      initialValues={{
        selected: entries
          .filter((row: [string, Record<string, unknown>]) => {
            const valueDetails = mapKeys(row[1], (_v, k) => camelCase(k)) as {
              value: string;
              approveStatus: boolean;
            };
            return valueDetails.approveStatus;
          })
          .map((row) => camelCase(row[0])),
        selectedFlexFields: entriesFlexFields
          .filter((row: [string, Record<string, unknown>]) => {
            const valueDetails = mapKeys(row[1], (_v, k) => camelCase(k)) as {
              value: string;
              approveStatus: boolean;
            };
            return valueDetails.approveStatus;
          })
          .map((row) => row[0]),
        selectedDocuments,
        selectedDocumentsToRemove,
        selectedDocumentsToEdit,
        selectedIdentities,
        selectedIdentitiesToEdit,
        selectedIdentitiesToRemove,
        selectedAccounts,
        selectedAccountsToEdit,

      }}
      onSubmit={async (values) => {
        const individualApproveData = values.selected.reduce((prev, curr) => {
          // eslint-disable-next-line no-param-reassign
          prev[curr] = true;
          return prev;
        }, {});
        const approvedDocumentsToCreate = values.selectedDocuments;
        const approvedDocumentsToRemove = values.selectedDocumentsToRemove;
        const approvedDocumentsToEdit = values.selectedDocumentsToEdit;
        const approvedIdentitiesToCreate = values.selectedIdentities;
        const approvedIdentitiesToRemove = values.selectedIdentitiesToRemove;
        const approvedIdentitiesToEdit = values.selectedIdentitiesToEdit;
        const approvedAccountsToCreate = values.selectedAccounts;
        const approvedAccountsToEdit = values.selectedAccountsToEdit;
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
              approvedDocumentsToEdit,
              approvedIdentitiesToCreate,
              approvedIdentitiesToRemove,
              approvedIdentitiesToEdit,
              approvedAccountsToCreate,
              approvedAccountsToEdit,
              flexFieldsApproveData: JSON.stringify(flexFieldsApproveData),
            },
          });
          showMessage('Changes Approved');
          const sum = Object.values(values).flat().length;
          setEdit(sum === 0);
        } catch (e) {
          e.graphQLErrors.map((x) => showMessage(x.message));
        }
      }}
    >
      {({ submitForm, setFieldValue, values }) => {
        const allChangesLength = Object.values(values).flat().length;

        return (
          <StyledBox>
            <Title>
              <Box display="flex" justifyContent="space-between">
                <Typography variant="h6">Requested Data Change</Typography>
                {shouldShowEditButton(allChangesLength) ? (
                  <Button
                    onClick={() => setEdit(true)}
                    variant="outlined"
                    color="primary"
                    disabled={ticket.status === GRIEVANCE_TICKET_STATES.CLOSED}
                  >
                    {t('EDIT')}
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
