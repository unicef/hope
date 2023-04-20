import React, { ReactElement, useState } from 'react';
<<<<<<< HEAD
import { useLocation } from 'react-router-dom';
=======
>>>>>>> develop
import {
  LookUpPaymentRecordsQueryVariables,
  PaymentRecordAndPaymentNode,
  useAllPaymentRecordsAndPaymentsQuery,
<<<<<<< HEAD
  useLookUpPaymentRecordsQuery,
=======
>>>>>>> develop
} from '../../../../__generated__/graphql';
import { UniversalTable } from '../../../../containers/tables/UniversalTable';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
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
  const businessArea = useBusinessArea();
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
    name: string,
  ): void => {
    const selectedIndex = selected.indexOf(name);
    const newSelected = [...selected];

    if (selectedIndex === -1) {
      newSelected.push(name);
    } else {
      newSelected.splice(selectedIndex, 1);
    }
    setSelected(newSelected);
    setFieldValue('selectedPaymentRecords', newSelected);
  };

  const handleSelectAllCheckboxesClick = (event, rows): void => {
    if (!selected.length) {
      const newSelecteds = rows.map((row) => row.id);
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
        queriedObjectName='allPaymentRecords'
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
      queriedObjectName='allPaymentRecordsAndPayments'
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
