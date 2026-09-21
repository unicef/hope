import { TableWrapper } from '@core/TableWrapper';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import type { GrievanceChoices } from '@restgenerated/models/GrievanceChoices';
import type { GrievanceTicketList } from '@restgenerated/models/GrievanceTicketList';
import type { PaginatedGrievanceTicketListList } from '@restgenerated/models/PaginatedGrievanceTicketListList';
import type { CountResponse } from '@restgenerated/models/CountResponse';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import { keepPreviousData, useQuery } from '@tanstack/react-query';
import { choicesToDict, dateToIsoString } from '@utils/utils';
import { createApiParams } from '@utils/apiUtils';
import type { MouseEvent, ReactElement } from 'react';
import { useState, useMemo } from 'react';
import { useDocumentTypeChoices } from '@hooks/useDocumentTypeChoices';
import { useTableState } from '@hooks/useTableState';
import { headCells } from './LookUpLinkedTicketsHeadCells';
import { LookUpLinkedTicketsTableRow } from './LookUpLinkedTicketsTableRow';

interface LookUpLinkedTicketsTableProps {
  businessArea: string;
  programId?: string;
  filter;
  setFieldValue;
  initialValues;
}

export function LookUpLinkedTicketsTable({
  businessArea,
  programId,
  filter,
  setFieldValue,
  initialValues,
}: LookUpLinkedTicketsTableProps): ReactElement {
  const { data: choicesData, isLoading: choicesLoading } =
    useQuery<GrievanceChoices>({
      queryKey: restQueryKey(RestService.restChoicesGrievanceTicketsRetrieve),
      queryFn: () => RestService.restChoicesGrievanceTicketsRetrieve(),
    });

  const { data: documentTypeChoices } = useDocumentTypeChoices();

  const filterVariables = useMemo(() => {
    return {
      businessAreaSlug: businessArea,
      programCode: programId,
      search: filter.search?.trim() || '',
      documentType: documentTypeChoices?.[0]?.value,
      documentNumber: filter.documentNumber?.trim() || '',
      status: filter.status ? [filter.status] : undefined,
      fsp: filter.fsp || undefined,
      createdAtAfter: dateToIsoString(filter.createdAtRangeMin, 'startOfDay'),
      createdAtBefore: dateToIsoString(filter.createdAtRangeMax, 'endOfDay'),
      admin2: filter?.admin2?.id,
    };
  }, [
    businessArea,
    programId,
    filter.search,
    filter.documentNumber,
    filter.status,
    filter.fsp,
    filter.createdAtRangeMin,
    filter.createdAtRangeMax,
    filter?.admin2?.id,
    documentTypeChoices,
  ]);

  const table = useTableState({
    rowsPerPageOptions: [10, 15, 20],
    resetPageOn: filterVariables,
  });
  const { page } = table;
  const listVariables = useMemo(
    () => ({ ...filterVariables, ...table.paginationParams }),
    [filterVariables, table.paginationParams],
  );

  const [selected, setSelected] = useState(initialValues.selectedLinkedTickets);

  const listParams = createApiParams(
    { businessAreaSlug: businessArea, programCode: programId },
    listVariables,
  );
  const countParams = createApiParams(
    { businessAreaSlug: businessArea, programCode: programId },
    filterVariables,
  );

  const { data, isLoading, isFetching, error } =
    useQuery<PaginatedGrievanceTicketListList>({
      queryKey: programId
        ? restQueryKey(
            RestService.restBusinessAreasProgramsGrievanceTicketsList,
            listParams,
          )
        : restQueryKey(
            RestService.restBusinessAreasGrievanceTicketsList,
            listParams,
          ),
      queryFn: () =>
        programId
          ? RestService.restBusinessAreasProgramsGrievanceTicketsList(
              listParams,
            )
          : RestService.restBusinessAreasGrievanceTicketsList(listParams),
      placeholderData: keepPreviousData,
      enabled: !choicesLoading && !!choicesData,
    });

  const { data: countData } = useQuery<CountResponse>({
    queryKey: programId
      ? restQueryKey(
          RestService.restBusinessAreasProgramsGrievanceTicketsCountRetrieve,
          countParams,
        )
      : restQueryKey(
          RestService.restBusinessAreasGrievanceTicketsCountRetrieve,
          countParams,
        ),
    queryFn: () =>
      programId
        ? RestService.restBusinessAreasProgramsGrievanceTicketsCountRetrieve(
            countParams,
          )
        : RestService.restBusinessAreasGrievanceTicketsCountRetrieve(
            countParams,
          ),
    enabled: !choicesLoading && !!choicesData && page === 0,
  });

  if (choicesLoading || !choicesData) {
    return null;
  }

  const statusChoices: {
    [id: number]: string;
  } = choicesToDict(choicesData.grievanceTicketStatusChoices);

  const categoryChoices: {
    [id: number]: string;
  } = choicesToDict(choicesData.grievanceTicketCategoryChoices);

  const handleCheckboxClick = (
    _event: MouseEvent<HTMLTableRowElement> | MouseEvent<HTMLButtonElement>,
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
    setFieldValue('selectedLinkedTickets', newSelected);
  };

  const handleSelectAllCheckboxesClick = (_event, rows): void => {
    if (!selected.length) {
      const newSelecteds = rows.map((row) => row.id);
      setSelected(newSelecteds);
      setFieldValue('selectedLinkedTickets', newSelecteds);

      return;
    }
    setSelected([]);
    setFieldValue('selectedLinkedTickets', []);
  };
  const numSelected = selected.length;

  const renderRow = (ticket: GrievanceTicketList): ReactElement => (
    <LookUpLinkedTicketsTableRow
      key={ticket.id}
      ticket={ticket}
      statusChoices={statusChoices}
      categoryChoices={categoryChoices}
      checkboxClickHandler={handleCheckboxClick}
      selected={selected}
    />
  );

  return (
    <TableWrapper>
      <UniversalRestTable
        headCells={headCells}
        onSelectAllClick={handleSelectAllCheckboxesClick}
        numSelected={numSelected}
        data={data}
        error={error}
        isLoading={isLoading}
        isFetching={isFetching}
        tableState={table}
        itemsCount={countData?.count}
        renderRow={renderRow}
      />
    </TableWrapper>
  );
}
