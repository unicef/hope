import type { MouseEvent, ReactElement } from 'react';
import { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useTableState } from '@hooks/useTableState';
import { headCells } from './LookUpPaymentRecordTableHeadCells';
import { LookUpPaymentRecordTableRow } from './LookUpPaymentRecordTableRow';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import type { PaginatedPaymentListList } from '@restgenerated/models/PaginatedPaymentListList';
import type { PaymentList } from '@restgenerated/models/PaymentList';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import { createApiParams } from '@utils/apiUtils';
import { keepPreviousData, useQuery } from '@tanstack/react-query';

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
  const isGlobal = programId === 'all' || !programId;
  const table = useTableState();
  const { page } = table;

  const globalPaymentsListParams = createApiParams(
    { businessAreaSlug: businessArea },
    table.paginationParams,
  );
  const programPaymentsListParams = createApiParams(
    {
      householdUnicefId: initialValues?.selectedHousehold?.unicefId,
      individualUnicefId: initialValues?.selectedIndividual?.unicefId,
      businessAreaSlug: businessArea,
      code: programId,
    },
    table.paginationParams,
  );
  const {
    data: paymentsData,
    isLoading,
    isFetching,
    error,
  } = useQuery<PaginatedPaymentListList>({
    queryKey: isGlobal
      ? restQueryKey(
          RestService.restBusinessAreasPaymentsList,
          globalPaymentsListParams,
        )
      : restQueryKey(
          RestService.restBusinessAreasProgramsPaymentsList,
          programPaymentsListParams,
        ),
    queryFn: () =>
      // Use global payments API when programId is 'all' or not available
      isGlobal
        ? RestService.restBusinessAreasPaymentsList(globalPaymentsListParams)
        : RestService.restBusinessAreasProgramsPaymentsList(
            programPaymentsListParams,
          ),
    placeholderData: keepPreviousData,
  });

  // Count queries for global and program payments
  const globalPaymentsCountParams = {
    businessAreaSlug: businessArea,
  };
  const { data: globalCountData } = useQuery({
    queryKey: restQueryKey(
      RestService.restBusinessAreasPaymentsCountRetrieve,
      globalPaymentsCountParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasPaymentsCountRetrieve(
        globalPaymentsCountParams,
      ),
    enabled: isGlobal && page === 0,
  });

  const programPaymentsCountParams = {
    householdUnicefId: initialValues?.selectedHousehold?.unicefId,
    individualUnicefId: initialValues?.selectedIndividual?.unicefId,
    businessAreaSlug: businessArea,
    code: programId,
  };
  const { data: programCountData } = useQuery({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsPaymentsCountRetrieve,
      programPaymentsCountParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentsCountRetrieve(
        programPaymentsCountParams,
      ),
    enabled: !isGlobal && page === 0,
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
        isFetching={isFetching}
        error={error}
        tableState={table}
        renderRow={(row: PaymentList) => (
          <LookUpPaymentRecordTableRow
            openInNewTab={openInNewTab}
            key={row.id}
            paymentRecord={row}
            checkboxClickHandler={handleCheckboxClick}
            selected={selected}
          />
        )}
        itemsCount={isGlobal ? globalCountData?.count : programCountData?.count}
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
      isFetching={isFetching}
      error={error}
      tableState={table}
      renderRow={(row) => (
        <LookUpPaymentRecordTableRow
          openInNewTab={openInNewTab}
          key={row.id}
          paymentRecord={row}
          checkboxClickHandler={handleCheckboxClick}
          selected={selected}
        />
      )}
      itemsCount={isGlobal ? globalCountData?.count : programCountData?.count}
    />
  );
}
