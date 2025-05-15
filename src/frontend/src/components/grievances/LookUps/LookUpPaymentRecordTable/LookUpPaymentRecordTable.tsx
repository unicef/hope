import { MouseEvent, ReactElement, useEffect, useMemo, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { headCells } from './LookUpPaymentRecordTableHeadCells';
import { LookUpPaymentRecordTableRow } from './LookUpPaymentRecordTableRow';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { PaginatedPaymentListList } from '@restgenerated/models/PaginatedPaymentListList';
import { PaymentList } from '@restgenerated/models/PaymentList';
import { RestService } from '@restgenerated/services/RestService';
import { createApiParams } from '@utils/apiUtils';
import { useQuery } from '@tanstack/react-query';

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
  const initialQueryVariables = useMemo(
    () => ({
      householdId: initialValues?.selectedHousehold?.id,
      businessAreaSlug: businessArea,
      slug: programId === 'all' ? null : programId,
    }),
    [initialValues?.selectedHousehold?.id, businessArea, programId],
  );

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

  const {
    data: paymentsData,
    isLoading,
    error,
  } = useQuery<PaginatedPaymentListList>({
    queryKey: [
      'businessAreasProgramsPaymentsList',
      queryVariables,
      initialValues?.selectedHousehold?.id,
      businessArea,
      programId,
    ],
    queryFn: () => {
      return RestService.restBusinessAreasProgramsPaymentsList(
        createApiParams(
          {
            householdId: initialValues?.selectedHousehold?.id,
            businessAreaSlug: businessArea,
            slug: programId === 'all' ? null : programId,
          },
          {},
          { withPagination: true },
        ),
      );
    },
  });
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
      <UniversalRestTable
        headCells={headCells}
        data={paymentsData}
        isLoading={isLoading}
        error={error}
        queryVariables={queryVariables}
        setQueryVariables={setQueryVariables}
        renderRow={(row: PaymentList) => (
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
    <UniversalRestTable
      headCells={headCells}
      onSelectAllClick={handleSelectAllCheckboxesClick}
      numSelected={numSelected}
      data={paymentsData}
      isLoading={isLoading}
      error={error}
      queryVariables={queryVariables}
      setQueryVariables={setQueryVariables}
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
