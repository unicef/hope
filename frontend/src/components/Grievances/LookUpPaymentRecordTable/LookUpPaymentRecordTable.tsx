import React, { ReactElement, useState } from 'react';
import { UniversalTable } from '../../../containers/tables/UniversalTable';
import {
  LookUpPaymentRecordsQueryVariables,
  PaymentRecordNode,
  useLookUpPaymentRecordsQuery,
} from '../../../__generated__/graphql';
import { headCells } from './LookUpPaymentRecordTableHeadCells';
import { LookUpPaymentRecordTableRow } from './LookUpPaymentRecordTableRow';

interface LookUpPaymentRecordTableProps {
  cashPlanId: string;
  openInNewTab?: boolean;
}
export function LookUpPaymentRecordTable({
  cashPlanId,
  openInNewTab = false,
}: LookUpPaymentRecordTableProps): ReactElement {
  const initialVariables = {
    cashPlan: cashPlanId,
  };
  const [selected, setSelected] = useState([]);

  const handleCheckboxClick = (event, name): void => {
    const selectedIndex = selected.indexOf(name);
    let newSelected = [];

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

    setSelected(newSelected);
  };

  const handleSelectAllCheckboxesClick = (event, rows): void => {
    if (event.target.checked) {
      const newSelecteds = rows.map((row) => row.id);
      setSelected(newSelecteds);
      return;
    }
    setSelected([]);
  };
  const numSelected = selected.length;
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
