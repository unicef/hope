import { TableWrapper } from '@components/core/TableWrapper';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { ProgramChoices } from '@restgenerated/models/ProgramChoices';
import { createApiParams } from '@utils/apiUtils';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { CountResponse } from '@restgenerated/models/CountResponse';
import { PaginatedProgramListList } from '@restgenerated/models/PaginatedProgramListList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { ReactElement, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { headCells } from './ProgrammesHeadCells';
import ProgrammesTableRow from './ProgrammesTableRow';
import { ProgramList } from '@restgenerated/models/ProgramList';

interface ProgrammesTableProps {
  businessArea: string;
  filter;
  choicesData: ProgramChoices;
}

function ProgrammesTable({
  businessArea,
  filter,
  choicesData,
}: ProgrammesTableProps): ReactElement {
  const { t } = useTranslation();
  const { programId, isAllPrograms } = useBaseUrl();

  const initialQueryVariables = useMemo(
    () => ({
      businessAreaSlug: businessArea,
      beneficiaryGroupMatch: isAllPrograms ? '' : programId,
      compatibleDct: isAllPrograms ? '' : programId,
      search: filter.search,
      startDate: filter.startDate || null,
      endDate: filter.endDate || null,
      status: filter.status !== '' ? filter.status : undefined,
      sector: filter.sector,
      numberOfHouseholdsMax: filter.numberOfHouseholdsMax,
      numberOfHouseholdsMin: filter.numberOfHouseholdsMin,
      budgetMax: filter.budgetMax,
      budgetMin: filter.budgetMin,
      dataCollectingType: filter.dataCollectingType,
      ordering: 'startDate',
    }),
    [
      businessArea,
      programId,
      isAllPrograms,
      filter.search,
      filter.startDate,
      filter.endDate,
      filter.status,
      filter.sector,
      filter.numberOfHouseholdsMin,
      filter.numberOfHouseholdsMax,
      filter.budgetMin,
      filter.budgetMax,
      filter.dataCollectingType,
    ],
  );

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

  const {
    data: dataPrograms,
    isLoading: isLoadingPrograms,
    error: errorPrograms,
  } = useQuery<PaginatedProgramListList>({
    queryKey: [
      'businessAreasProgramsList',
      queryVariables,
      businessArea,
      programId,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsList(
        createApiParams({ businessAreaSlug: businessArea }, queryVariables, {
          withPagination: true,
        }),
      ),
    enabled: !!queryVariables.businessAreaSlug,
  });

  const { data: dataProgramsCount } = useQuery<CountResponse>({
    queryKey: ['businessAreasProgramsCount', businessArea],
    queryFn: () =>
      RestService.restBusinessAreasProgramsCountRetrieve({
        businessAreaSlug: businessArea,
      }),
  });

  return (
    <>
      <TableWrapper>
        <UniversalRestTable
          title={t('Programmes')}
          headCells={headCells}
          queryVariables={queryVariables}
          setQueryVariables={setQueryVariables}
          defaultOrderBy="startDate"
          data={dataPrograms}
          isLoading={isLoadingPrograms}
          error={errorPrograms}
          itemsCount={dataProgramsCount?.count}
          renderRow={(row: ProgramList) => (
            <ProgrammesTableRow
              key={row.id}
              program={row}
              choicesData={choicesData}
            />
          )}
        />
      </TableWrapper>
    </>
  );
}
export default withErrorBoundary(ProgrammesTable, 'ProgrammesTable');
