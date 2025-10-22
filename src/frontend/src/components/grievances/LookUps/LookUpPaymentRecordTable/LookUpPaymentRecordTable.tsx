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

  // Separate page state for global and program payments
  const [globalPage, setGlobalPage] = useState(0);
  const [programPage, setProgramPage] = useState(0);

  const {
    data: paymentsData,
    isLoading,
    error,
  } = useQuery<PaginatedPaymentListList>({
    queryKey: [
      programId === 'all' || !programId
        ? 'businessAreasPaymentsList'
        : 'businessAreasProgramsPaymentsList',
      queryVariables,
      initialValues?.selectedHousehold?.id,
      businessArea,
      programId,
      programId === 'all' || !programId ? globalPage : programPage,
    ],
    queryFn: () => {
      // Use global payments API when programId is 'all' or not available
      if (programId === 'all' || !programId) {
        return RestService.restBusinessAreasPaymentsList(
          createApiParams(
            {
              householdId: initialValues?.selectedHousehold?.id,
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
            householdId: initialValues?.selectedHousehold?.id,
            businessAreaSlug: businessArea,
            slug: programId,
          },
          {},
          { withPagination: true },
        ),
      );
    },
  });

  // Count queries for global and program payments
  const { data: globalCountData } = useQuery({
    queryKey: [
      'businessAreasPaymentsCount',
      queryVariables,
      initialValues?.selectedHousehold?.id,
      businessArea,
      globalPage,
    ],
    queryFn: () =>
      RestService.restBusinessAreasPaymentsCountRetrieve(
        createApiParams(
          {
            householdId: initialValues?.selectedHousehold?.id,
            businessAreaSlug: businessArea,
          },
          {},
        ),
      ),
    enabled: (programId === 'all' || !programId) && globalPage === 0,
  });

  const { data: programCountData } = useQuery({
    queryKey: [
      'businessAreasProgramsPaymentPlansPaymentsCount',
      queryVariables,
      initialValues?.selectedHousehold?.id,
      businessArea,
      programId,
      programPage,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlansPaymentsCountRetrieve(
        createApiParams(
          {
            householdId: initialValues?.selectedHousehold?.id,
            businessAreaSlug: businessArea,
            paymentPlanPk: programId,
            programSlug: programId,
          },
          {},
        ),
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
