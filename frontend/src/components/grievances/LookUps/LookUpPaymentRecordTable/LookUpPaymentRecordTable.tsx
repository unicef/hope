import React, { ReactElement, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { UniversalTable } from '../../../../containers/tables/UniversalTable';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import {
  LookUpPaymentRecordsQueryVariables,
  PaymentRecordNode,
  useLookUpPaymentRecordsQuery,
} from '../../../../__generated__/graphql';
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

  const handleCheckboxClick = (event, name): void => {
    const selectedIndex = selected.indexOf(name);
    let newSelected = [];
    if (!isEditTicket) {
      if (selectedIndex === -1) {
        newSelected = newSelected.concat(selected, name);
      } else if (selectedIndex === 0) {
        newSelected = newSelected.concat(selected.slice(1));
      } else if (selectedIndex === selected.length - 1) {
        newSelected = newSelected.concat(selected.slice(0, -1));
      } else if (selectedIndex > 0) {
        newSelected = newSelected.concat(
          selected.slice(0, selectedIndex),
          selected.slice(selectedIndex + 1),
        );
      }
    } else {
      newSelected = [name];
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
      <UniversalTable<PaymentRecordNode, LookUpPaymentRecordsQueryVariables>
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
    <UniversalTable<PaymentRecordNode, LookUpPaymentRecordsQueryVariables>
      headCells={headCells}
      query={useLookUpPaymentRecordsQuery}
      queriedObjectName='allPaymentRecords'
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
