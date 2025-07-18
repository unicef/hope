import { ReactElement, useMemo, useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useQuery } from '@tanstack/react-query';
import { TableWrapper } from '@components/core/TableWrapper';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { dateToIsoString, decodeIdString } from '@utils/utils';
import { createApiParams } from '@utils/apiUtils';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { RestService } from '@restgenerated/services/RestService';
import { PaginatedRegistrationDataImportListList } from '@restgenerated/models/PaginatedRegistrationDataImportListList';
import { RegistrationDataImportList } from '@restgenerated/models/RegistrationDataImportList';
import { headCells } from './RegistrationDataImportForPeopleTableHeadCells';
import { RegistrationDataImportForPeopleTableRow } from './RegistrationDataImportForPeopleTableRow';

interface RegistrationDataImportForPeopleTableProps {
  filter;
  canViewDetails: boolean;
  enableRadioButton?: boolean;
  selectedRDI?;
  handleChange?;
  noTableStyling?;
  noTitle?;
}

const NoTableStyling = styled.div`
  .MuiPaper-elevation1 {
    box-shadow: none;
    padding: 0 !important;
  }
`;

export function RegistrationDataImportForPeopleTable({
  filter,
  canViewDetails,
  enableRadioButton,
  selectedRDI,
  handleChange,
  noTableStyling,
  noTitle,
}: RegistrationDataImportForPeopleTableProps): ReactElement {
  const { t } = useTranslation();
  const { businessArea, programSlug } = useBaseUrl();

  const initialQueryVariables = useMemo(
    () => ({
      search: filter.search,
      importedById: filter.importedBy
        ? decodeIdString(filter.importedBy)
        : undefined,
      status: filter.status !== '' ? filter.status : undefined,
      importDateRange: JSON.stringify({
        min: dateToIsoString(filter.importDateRangeMin, 'startOfDay'),
        max: dateToIsoString(filter.importDateRangeMax, 'endOfDay'),
      }),
      size: JSON.stringify({ min: filter.sizeMin, max: filter.sizeMax }),
    }),
    [
      filter.search,
      filter.importedBy,
      filter.status,
      filter.importDateRangeMin,
      filter.importDateRangeMax,
      filter.sizeMin,
      filter.sizeMax,
    ],
  );

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

  const { data, isLoading, error } =
    useQuery<PaginatedRegistrationDataImportListList>({
      queryKey: [
        'businessAreasProgramsRegistrationDataImportsList',
        businessArea,
        programSlug,
        queryVariables,
      ],
      queryFn: () =>
        RestService.restBusinessAreasProgramsRegistrationDataImportsList(
          createApiParams(
            { businessAreaSlug: businessArea, programSlug },
            queryVariables,
            { withPagination: true },
          ),
        ),
    });

  const handleRadioChange = (id: string): void => {
    handleChange(id);
  };

  const renderTable = (): ReactElement => (
    <TableWrapper>
      <UniversalRestTable<RegistrationDataImportList, any>
        title={noTitle ? null : t('List of Imports')}
        getTitle={(tableData) =>
          noTitle ? null : `${t('List of Imports')} (${tableData?.count || 0})`
        }
        headCells={enableRadioButton ? headCells : headCells.slice(1)}
        defaultOrderBy="importDate"
        defaultOrderDirection="desc"
        rowsPerPageOptions={[10, 15, 20]}
        data={data}
        isLoading={isLoading}
        error={error}
        queryVariables={queryVariables}
        setQueryVariables={setQueryVariables}
        renderRow={(row) => (
          <RegistrationDataImportForPeopleTableRow
            key={row.id}
            radioChangeHandler={enableRadioButton && handleRadioChange}
            selectedRDI={selectedRDI}
            registrationDataImport={row}
            canViewDetails={canViewDetails}
          />
        )}
      />
    </TableWrapper>
  );
  return noTableStyling ? (
    <NoTableStyling>{renderTable()}</NoTableStyling>
  ) : (
    renderTable()
  );
}
