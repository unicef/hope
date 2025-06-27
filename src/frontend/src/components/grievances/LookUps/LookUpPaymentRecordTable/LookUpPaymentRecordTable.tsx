import { MouseEvent, ReactElement, useState } from 'react';
import { useLocation } from 'react-router-dom';
import {
  AllPaymentsForTableQueryVariables,
  PaymentNode,
  useAllPaymentsForTableQuery,
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
  const { businessArea, programId } = useBaseUrl();
  const location = useLocation();
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;
  const initialVariables = {
    householdId: initialValues?.selectedHousehold?.id,
    businessArea,
    program: programId === 'all' ? null : programId,
  };
  const [selected, setSelected] = useState(
    initialValues.selectedPaymentRecords,
  );

  const handleCheckboxClick = (
    _event: MouseEvent<HTMLTableRowElement> | MouseEvent<HTMLButtonElement>,
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
      <UniversalTable<PaymentNode, AllPaymentsForTableQueryVariables>
        headCells={headCells}
        query={useAllPaymentsForTableQuery}
        queriedObjectName="allPayments"
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
    <UniversalTable<PaymentNode, AllPaymentsForTableQueryVariables>
      headCells={headCells}
      query={useAllPaymentsForTableQuery}
      queriedObjectName="allPayments"
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
