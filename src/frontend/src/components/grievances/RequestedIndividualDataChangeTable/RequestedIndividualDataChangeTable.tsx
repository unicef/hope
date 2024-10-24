import { ReactElement } from 'react';
import { useArrayToDict } from '@hooks/useArrayToDict';
import {
  GrievanceTicketQuery,
  useAllAddIndividualFieldsQuery,
} from '@generated/graphql';
import { LoadingComponent } from '@core/LoadingComponent';
import { DocumentsTable } from './DocumentsTable';
import { DocumentsToEditTable } from './DocumentsToEditTable';
import { DocumentsToRemoveTable } from './DocumentsToRemoveTable';
import { EntriesTable } from './EntriesTable';
import { IdentitiesTable } from './IdentitiesTable';
import { IdentitiesToEditTable } from './IdentitiesToEditTable';
import { IdentitiesToRemoveTable } from './IdentitiesToRemoveTable';
import { PaymentChannelsTable } from './PaymentChannelsTable';
import { PaymentChannelsToEditTable } from './PaymentChannelsToEditTable';
import { PaymentChannelsToRemoveTable } from './PaymentChannelsToRemoveTable';
import { DeliveryMechanismDataToEditTable } from './DeliveryMechanismDataToEditTable';

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
  const {
    documents,
    identities,
    previous_documents: previousDocuments,
    documents_to_remove: documentsToRemove,
    documents_to_edit: documentsToEdit,
    previous_identities: previousIdentities,
    identities_to_remove: identitiesToRemove,
    identities_to_edit: identitiesToEdit,
    payment_channels: paymentChannels,
    payment_channels_to_remove: paymentChannelsToRemove,
    payment_channels_to_edit: paymentChannelsToEdit,
    previous_payment_channels: previousPaymentChannels,
    flex_fields: flexFields,
    delivery_mechanism_data: deliveryMechanismData,
    delivery_mechanism_data_to_edit: deliveryMechanismDataToEdit,
    delivery_mechanism_data_to_remove: deliveryMechanismDataToRemove,
    ...restIndividualData
  } = individualData;
  const entries = restIndividualData && Object.entries(restIndividualData);
  const entriesFlexFields = flexFields && Object.entries(flexFields);
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
      {entries?.length || entriesFlexFields?.length ? (
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
      {paymentChannels?.length ? (
        <PaymentChannelsTable
          values={values}
          isEdit={isEdit}
          ticket={ticket}
          setFieldValue={setFieldValue}
          paymentChannels={paymentChannels}
        />
      ) : null}
      {paymentChannelsToEdit?.length
        ? paymentChannelsToEdit.map((paymentChannel, index) => (
            <PaymentChannelsToEditTable
              key={paymentChannel.previous_value.bankAccountNumber}
              values={values}
              isEdit={isEdit}
              ticket={ticket}
              setFieldValue={setFieldValue}
              index={index}
              paymentChannel={paymentChannel}
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
      {paymentChannelsToRemove?.length ? (
        <PaymentChannelsToRemoveTable
          values={values}
          isEdit={isEdit}
          ticket={ticket}
          setFieldValue={setFieldValue}
          paymentChannelsToRemove={paymentChannelsToRemove}
          previousPaymentChannels={previousPaymentChannels}
        />
      ) : null}
      {deliveryMechanismDataToEdit?.length
        ? deliveryMechanismDataToEdit.map(
            (deliveryMechanismDataItem, index) => (
              <DeliveryMechanismDataToEditTable
                key={deliveryMechanismDataItem?.id}
                values={values}
                isEdit={isEdit}
                ticket={ticket}
                index={index}
                setFieldValue={setFieldValue}
                deliveryMechanismDataToEdit={deliveryMechanismDataItem}
              />
            ),
          )
        : null}
    </div>
  );
}
