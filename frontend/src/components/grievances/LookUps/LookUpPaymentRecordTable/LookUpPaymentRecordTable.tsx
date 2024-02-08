import { ReactElement, useState } from 'react';
import { useLocation } from 'react-router-dom';
import {
  LookUpPaymentRecordsQueryVariables,
  PaymentRecordAndPaymentNode,
  useAllPaymentRecordsAndPaymentsQuery,
  useLookUpPaymentRecordsQuery,
} from '@generated/graphql';
import { UniversalTable } from '@containers/tables/UniversalTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { headCells } from './LookUpPaymentRecordTableHeadCells';
import { LookUpPaymentRecordTableRow } from './LookUpPaymentRecordTableRow';

interface LookUpPaymentRecordTableProps {
  openInNewTab?: boolean;
  setFieldValue;
  initialValues;
}
export function LookUpPaymentRecordTable({
  openInNewTab = false,
  setFieldValue,
  initialValues,
}: LookUpPaymentRecordTableProps): ReactElement {
  const { businessArea } = useBaseUrl();
  const location = useLocation();
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;
  const initialVariables = {
    household: initialValues?.selectedHousehold?.id,
    businessArea,
  };
  const [selected, setSelected] = useState(
    initialValues.selectedPaymentRecords,
  );

  const handleCheckboxClick = (
    _event:
      | React.MouseEvent<HTMLButtonElement, MouseEvent>
      | React.MouseEvent<HTMLTableRowElement, MouseEvent>,
    selectedPaymentRecord,
  ): void => {
    const selectedIndex = selected.indexOf(selectedPaymentRecord);
    const newSelected = [...selected];

    if (selectedIndex === -1) {
      newSelected.push(selectedPaymentRecord);
    } else {
      newSelected.splice(selectedIndex, 1);
    }
    setSelected(newSelected);
    setFieldValue('selectedPaymentRecords', newSelected);
  };

  const handleSelectAllCheckboxesClick = (_, rows): void => {
    if (!selected.length) {
      const newSelecteds = rows;
      setSelected(newSelecteds);
      setFieldValue('selectedPaymentRecords', newSelecteds);
      return;
    }
    setSelected([]);
    setFieldValue('selectedPaymentRecords', []);
  };
  const numSelected = selected.length;

  if (isEditTicket) {
    return (
      <UniversalTable<
        PaymentRecordAndPaymentNode,
        LookUpPaymentRecordsQueryVariables
      >
        headCells={headCells}
        query={useLookUpPaymentRecordsQuery}
        queriedObjectName="allPaymentRecords"
        initialVariables={initialVariables}
        renderRow={(row) => (
          <LookUpPaymentRecordTableRow
            openInNewTab={openInNewTab}
            key={row.id}
            paymentRecord={row}
            checkboxClickHandler={handleCheckboxClick}
            selected={selected}
          />
        )}
      />
    );
  }
  return (
    <UniversalTable<
      PaymentRecordAndPaymentNode,
      LookUpPaymentRecordsQueryVariables
    >
      headCells={headCells}
      query={useAllPaymentRecordsAndPaymentsQuery}
      queriedObjectName="allPaymentRecordsAndPayments"
      initialVariables={initialVariables}
      onSelectAllClick={handleSelectAllCheckboxesClick}
      numSelected={numSelected}
      renderRow={(row) => (
        <LookUpPaymentRecordTableRow
          openInNewTab={openInNewTab}
          key={row.id}
          paymentRecord={row}
          checkboxClickHandler={handleCheckboxClick}
          selected={selected}
        />
      )}
    />
  );
}
