import { MouseEvent, ReactElement, useEffect, useMemo, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { headCells } from './LookUpPaymentRecordTableHeadCells';
import { LookUpPaymentRecordTableRow } from './LookUpPaymentRecordTableRow';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { PaginatedPaymentListList } from '@restgenerated/models/PaginatedPaymentListList';
import { PaymentList } from '@restgenerated/models/PaymentList';
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
  const initialQueryVariables = useMemo(
    () => ({
      householdUnicefId: initialValues?.selectedHousehold?.unicefId,
      individualUnicefId: initialValues?.selectedIndividual?.unicefId,
      businessAreaSlug: businessArea,
      code: programId === 'all' ? null : programId,
    }),
    [
      initialValues?.selectedHousehold?.unicefId,
      initialValues?.selectedIndividual?.unicefId,
      businessArea,
      programId,
    ],
  );

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

  // Separate page state for global and program payments
  const [globalPage, setGlobalPage] = useState(0);
  const [programPage, setProgramPage] = useState(0);

  const {
    data: paymentsData,
    isLoading,
    isFetching,
    error,
  } = useQuery<PaginatedPaymentListList>({
    queryKey:
      programId === 'all' || !programId
        ? restQueryKey(
            RestService.restBusinessAreasPaymentsList,
            createApiParams(
              {
                businessAreaSlug: businessArea,
              },
              {},
              { withPagination: true },
            ),
          )
        : restQueryKey(
            RestService.restBusinessAreasProgramsPaymentsList,
            createApiParams(
              {
                householdUnicefId: initialValues?.selectedHousehold?.unicefId,
                individualUnicefId:
                  initialValues?.selectedIndividual?.unicefId,
                businessAreaSlug: businessArea,
                code: programId,
              },
              {},
              { withPagination: true },
            ),
          ),
    queryFn: () => {
      // Use global payments API when programId is 'all' or not available
      if (programId === 'all' || !programId) {
        return RestService.restBusinessAreasPaymentsList(
          createApiParams(
            {
              businessAreaSlug: businessArea,
            },
            {},
            { withPagination: true },
          ),
        );
      }
      // Use program-specific payments API when programId is available
      return RestService.restBusinessAreasProgramsPaymentsList(
        createApiParams(
          {
            householdUnicefId: initialValues?.selectedHousehold?.unicefId,
            individualUnicefId: initialValues?.selectedIndividual?.unicefId,
            businessAreaSlug: businessArea,
            code: programId,
          },
          {},
          { withPagination: true },
        ),
      );
    },
    placeholderData: keepPreviousData,
  });

  // Count queries for global and program payments
  const globalPaymentsCountParams = createApiParams(
    {
      businessAreaSlug: businessArea,
    },
    {},
  );
  const { data: globalCountData } = useQuery({
    queryKey: restQueryKey(
      RestService.restBusinessAreasPaymentsCountRetrieve,
      globalPaymentsCountParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasPaymentsCountRetrieve(
        globalPaymentsCountParams,
      ),
    enabled: (programId === 'all' || !programId) && globalPage === 0,
  });

  const programPaymentsCountParams = createApiParams(
    {
      householdUnicefId: initialValues?.selectedHousehold?.unicefId,
      individualUnicefId: initialValues?.selectedIndividual?.unicefId,
      businessAreaSlug: businessArea,
      code: programId,
    },
    {},
  );
  const { data: programCountData } = useQuery({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsPaymentsCountRetrieve,
      programPaymentsCountParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentsCountRetrieve(
        programPaymentsCountParams,
      ),
    enabled: programId !== 'all' && !!programId && programPage === 0,
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
        page={programId === 'all' || !programId ? globalPage : programPage}
        setPage={
          programId === 'all' || !programId ? setGlobalPage : setProgramPage
        }
        itemsCount={
          programId === 'all' || !programId
            ? globalCountData?.count
            : programCountData?.count
        }
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
      page={programId === 'all' || !programId ? globalPage : programPage}
      setPage={
        programId === 'all' || !programId ? setGlobalPage : setProgramPage
      }
      itemsCount={
        programId === 'all' || !programId
          ? globalCountData?.count
          : programCountData?.count
      }
    />
  );
}
