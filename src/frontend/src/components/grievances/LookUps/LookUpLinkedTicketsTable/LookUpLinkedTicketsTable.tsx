import { TableWrapper } from '@core/TableWrapper';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { GrievanceChoices } from '@restgenerated/models/GrievanceChoices';
import { GrievanceTicketList } from '@restgenerated/models/GrievanceTicketList';
import { PaginatedGrievanceTicketListList } from '@restgenerated/models/PaginatedGrievanceTicketListList';
import { CountResponse } from '@restgenerated/models/CountResponse';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { choicesToDict, dateToIsoString } from '@utils/utils';
import { createApiParams } from '@utils/apiUtils';
import { MouseEvent, ReactElement, useState, useEffect, useMemo } from 'react';
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
      queryKey: ['businessAreasGrievanceTicketsChoices', businessArea],
      queryFn: () =>
        RestService.restBusinessAreasGrievanceTicketsChoicesRetrieve({
          businessAreaSlug: businessArea,
        }),
    });

  const initialQueryVariables = useMemo(() => {
    return {
      businessAreaSlug: businessArea,
      programSlug: programId,
      search: filter.search?.trim() || '',
      documentType: choicesData?.documentTypeChoices?.[0]?.value,
      documentNumber: filter.documentNumber?.trim() || '',
      status: filter.status ? [filter.status] : undefined,
      fsp: filter.fsp || undefined,
      createdAtAfter: dateToIsoString(filter.createdAtRangeMin, 'startOfDay'),
      createdAtBefore: dateToIsoString(filter.createdAtRangeMax, 'endOfDay'),
      admin2: filter?.admin2?.node?.id,
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
    filter?.admin2?.node?.id,
    choicesData?.documentTypeChoices,
  ]);

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

  const [selected, setSelected] = useState(initialValues.selectedLinkedTickets);

  const { data, isLoading, error } = useQuery<PaginatedGrievanceTicketListList>(
    {
      queryKey: [
        programId
          ? 'businessAreasProgramsGrievanceTicketsList'
          : 'businessAreasGrievanceTicketsList',
        queryVariables,
        businessArea,
        programId,
      ],
      queryFn: () => {
        if (programId) {
          return RestService.restBusinessAreasProgramsGrievanceTicketsList(
            createApiParams(
              { businessAreaSlug: businessArea, programSlug: programId },
              queryVariables,
              { withPagination: true },
            ),
          );
        } else {
          return RestService.restBusinessAreasGrievanceTicketsList(
            createApiParams(
              { businessAreaSlug: businessArea },
              queryVariables,
              { withPagination: true },
            ),
          );
        }
      },
      enabled: !choicesLoading && !!choicesData,
    },
  );

  const { data: countData } = useQuery<CountResponse>({
    queryKey: [
      programId
        ? 'businessAreasProgramsGrievanceTicketsCount'
        : 'businessAreasGrievanceTicketsCount',
      businessArea,
      programId,
    ],
    queryFn: () => {
      if (programId) {
        return RestService.restBusinessAreasProgramsGrievanceTicketsCountRetrieve(
          {
            businessAreaSlug: businessArea,
            programSlug: programId,
          },
        );
      } else {
        return RestService.restBusinessAreasGrievanceTicketsCountRetrieve({
          businessAreaSlug: businessArea,
        });
      }
    },
    enabled: !choicesLoading && !!choicesData,
  });

  if (choicesLoading) {
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
        rowsPerPageOptions={[10, 15, 20]}
        onSelectAllClick={handleSelectAllCheckboxesClick}
        numSelected={numSelected}
        data={data}
        error={error}
        isLoading={isLoading}
        queryVariables={queryVariables}
        setQueryVariables={setQueryVariables}
        itemsCount={countData?.count}
        renderRow={renderRow}
      />
    </TableWrapper>
  );
}
