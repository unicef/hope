import { ReactElement } from 'react';
import { useArrayToDict } from '@hooks/useArrayToDict';
import { LoadingComponent } from '@core/LoadingComponent';
import { DocumentsTable } from './DocumentsTable';
import { DocumentsToEditTable } from './DocumentsToEditTable';
import { DocumentsToRemoveTable } from './DocumentsToRemoveTable';
import { EntriesTable } from './EntriesTable';
import { IdentitiesTable } from './IdentitiesTable';
import { IdentitiesToEditTable } from './IdentitiesToEditTable';
import { IdentitiesToRemoveTable } from './IdentitiesToRemoveTable';
import { AccountToEditTable } from './AccountToEditTable';
import { AccountTable } from './AccountTable';
import { PaymentChannelsTable } from './PaymentChannelsTable';
import { PaymentChannelsToEditTable } from './PaymentChannelsToEditTable';
import { PaymentChannelsToRemoveTable } from './PaymentChannelsToRemoveTable';
import { GrievanceTicketDetail } from '@restgenerated/models/GrievanceTicketDetail';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useHopeDetailsQuery } from '@hooks/useHopeDetailsQuery';
import { IndividualDetail } from '@restgenerated/models/IndividualDetail';

interface RequestedIndividualDataChangeTableProps {
  ticket: GrievanceTicketDetail;
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
  const { businessAreaSlug } = useBaseUrl();

  const { data: addIndividualFieldsData, isLoading: loading } = useQuery({
    queryKey: ['addIndividualFieldsAttributes', businessAreaSlug],
    queryFn: () =>
      RestService.restBusinessAreasGrievanceTicketsAllAddIndividualsFieldsAttributesList(
        {
          businessAreaSlug,
        },
      ),
  });

  const { data: individualChoicesData, isLoading: individualChoicesLoading } =
    useQuery({
      queryKey: ['individualChoices', businessAreaSlug],
      queryFn: () =>
        RestService.restBusinessAreasIndividualsChoicesRetrieve({
          businessAreaSlug,
        }),
    });

  const { data: countriesData, isLoading: countriesLoading } = useQuery({
    queryKey: ['countriesList'],
    queryFn: () => RestService.restChoicesCountriesList(),
  });

  const { data: individual, isLoading: individualLoading } =
    useHopeDetailsQuery<IndividualDetail>(
      ticket.individual.id,
      RestService.restBusinessAreasProgramsIndividualsRetrieve,
      {},
    );

  const individualData = {
    ...ticket.ticketDetails.individualData,
  };
  const {
    documents,
    identities,
    previous_documents: previousDocuments,
    documents_to_remove: documentsToRemove,
    documents_to_edit: documentsToEdit,
    previous_identities: previousIdentities,
    identities_to_remove: identitiesToRemove,
    identities_to_edit: identitiesToEdit,
    accounts: accounts,
    accounts_to_edit: accountsToEdit,
    flex_fields: flexFields,
    ...restIndividualData
  } = individualData;
  const entries = restIndividualData && Object.entries(restIndividualData);
  const entriesFlexFields = flexFields && Object.entries(flexFields);
  //@ts-ignore
  const fieldsDict = useArrayToDict(addIndividualFieldsData, 'name', '*');
  const countriesDict = useArrayToDict(countriesData, 'name', 'value');
  const documentTypeDict = useArrayToDict(
    individualChoicesData?.documentTypeChoices,
    'value',
    'name',
  );
  const identityTypeDict = useArrayToDict(
    individualChoicesData?.identityTypeChoices,
    'value',
    'name',
  );

  if (
    loading ||
    individualChoicesLoading ||
    countriesLoading ||
    !fieldsDict ||
    !countriesDict ||
    !documentTypeDict ||
    !identityTypeDict ||
    individualLoading
  ) {
    return <LoadingComponent />;
  }

  return (
    <div>
      {entries?.length || entriesFlexFields?.length ? (
        <EntriesTable
          values={values}
          isEdit={isEdit}
          fieldsDict={fieldsDict}
          countriesDict={countriesDict}
          ticket={ticket}
          entries={entries}
          entriesFlexFields={entriesFlexFields}
          setFieldValue={setFieldValue}
          individual={individual}
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
        ? identitiesToEdit.map((identity, index) => (
            <IdentitiesToEditTable
              key={identity.previous_value.number}
              values={values}
              isEdit={isEdit}
              ticket={ticket}
              setFieldValue={setFieldValue}
              countriesDict={countriesDict}
              index={index}
              identity={identity}
            />
          ))
        : null}
      {accounts?.length ? accounts.map((account, index) => (
        <AccountTable
          key={account.id}
          values={values}
          isEdit={isEdit}
          ticket={ticket}
          setFieldValue={setFieldValue}
          index={index}
          account={account}
        />
      )) : null}
      {accountsToEdit?.length
        ? accountsToEdit.map((account, index) => (
            <AccountToEditTable
              key={account.id}
              values={values}
              isEdit={isEdit}
              ticket={ticket}
              setFieldValue={setFieldValue}
              index={index}
              account={account}
            />
          ))
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
