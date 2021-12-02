import React, { ReactElement } from 'react';
import { useArrayToDict } from '../../../hooks/useArrayToDict';
import {
  GrievanceTicketQuery,
  useAllAddIndividualFieldsQuery,
} from '../../../__generated__/graphql';
import { LoadingComponent } from '../../LoadingComponent';
import { DocumentsTable } from './DocumentsTable';
import { DocumentsToEditTable } from './DocumentsToEditTable';
import { DocumentsToRemoveTable } from './DocumentsToRemoveTable';
import { EntriesTable } from './EntriesTable';
import { IdentitiesTable } from './IdentitiesTable';
import { IdentitiesToEditTable } from './IdentitiesToEditTable';
import { IdentitiesToRemoveTable } from './IdentitiesToRemoveTable';

interface RequestedIndividualDataChangeTableProps {
  ticket: GrievanceTicketQuery['grievanceTicket'];
  setFieldValue;
  values;
  isEdit;
}

export function RequestedIndividualDataChangeTable({
  setFieldValue,
  ticket,
  values,
  isEdit,
}: RequestedIndividualDataChangeTableProps): ReactElement {
  const { data, loading } = useAllAddIndividualFieldsQuery();
  const individualData = {
    ...ticket.individualDataUpdateTicketDetails.individualData,
  };
  const documents = individualData?.documents;
  const previousDocuments = individualData.previous_documents;
  const documentsToRemove = individualData.documents_to_remove;
  const documentsToEdit = individualData.documents_to_edit;
  const identities = individualData?.identities;
  const previousIdentities = individualData.previous_identities;
  const identitiesToRemove = individualData.identities_to_remove;
  const identitiesToEdit = individualData.identities_to_edit;
  const flexFields = individualData.flex_fields;
  delete individualData.documents;
  delete individualData.documents_to_remove;
  delete individualData.previous_documents;
  delete individualData.documents_to_edit;
  delete individualData.identities;
  delete individualData.identities_to_remove;
  delete individualData.identities_to_edit;
  delete individualData.previous_identities;
  delete individualData.flex_fields;
  const entries = Object.entries(individualData);
  const entriesFlexFields = Object.entries(flexFields);
  const fieldsDict = useArrayToDict(
    data?.allAddIndividualsFieldsAttributes,
    'name',
    '*',
  );
  const countriesDict = useArrayToDict(data?.countriesChoices, 'value', 'name');
  const documentTypeDict = useArrayToDict(
    data?.documentTypeChoices,
    'value',
    'name',
  );
  const identityTypeDict = useArrayToDict(
    data?.identityTypeChoices,
    'value',
    'name',
  );

  if (
    loading ||
    !fieldsDict ||
    !countriesDict ||
    !documentTypeDict ||
    !identityTypeDict
  ) {
    return <LoadingComponent />;
  }

  return (
    <div>
      {entries?.length ? (
        <EntriesTable
          values={values}
          isEdit={isEdit}
          fieldsDict={fieldsDict}
          ticket={ticket}
          entries={entries}
          entriesFlexFields={entriesFlexFields}
          setFieldValue={setFieldValue}
        />
      ) : null}
      {documents?.length ? (
        <DocumentsTable
          values={values}
          isEdit={isEdit}
          ticket={ticket}
          documents={documents}
          setFieldValue={setFieldValue}
          documentTypeDict={documentTypeDict}
          countriesDict={countriesDict}
        />
      ) : null}
      {documentsToEdit?.length
        ? documentsToEdit.map((document, index) => (
            <DocumentsToEditTable
              key={document.previous_value.number}
              values={values}
              isEdit={isEdit}
              ticket={ticket}
              setFieldValue={setFieldValue}
              documentTypeDict={documentTypeDict}
              countriesDict={countriesDict}
              index={index}
              document={document}
            />
          ))
        : null}
      {identities?.length ? (
        <IdentitiesTable
          values={values}
          isEdit={isEdit}
          ticket={ticket}
          setFieldValue={setFieldValue}
          documentTypeDict={documentTypeDict}
          countriesDict={countriesDict}
          identityTypeDict={identityTypeDict}
          document={document}
          identities={identities}
        />
      ) : null}
      {identitiesToEdit?.length
        ? identitiesToEdit.map((identity, index) => {
            return (
              <IdentitiesToEditTable
                values={values}
                isEdit={isEdit}
                ticket={ticket}
                setFieldValue={setFieldValue}
                countriesDict={countriesDict}
                index={index}
                identity={identity}
              />
            );
          })
        : null}
      {documentsToRemove?.length ? (
        <DocumentsToRemoveTable
          values={values}
          isEdit={isEdit}
          ticket={ticket}
          setFieldValue={setFieldValue}
          countriesDict={countriesDict}
          documentsToRemove={documentsToRemove}
          previousDocuments={previousDocuments}
        />
      ) : null}
      {identitiesToRemove?.length ? (
        <IdentitiesToRemoveTable
          values={values}
          isEdit={isEdit}
          ticket={ticket}
          setFieldValue={setFieldValue}
          countriesDict={countriesDict}
          identitiesToRemove={identitiesToRemove}
          previousIdentities={previousIdentities}
        />
      ) : null}
    </div>
  );
}
