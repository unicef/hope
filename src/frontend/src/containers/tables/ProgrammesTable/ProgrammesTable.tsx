import { TableWrapper } from '@components/core/TableWrapper';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { ProgrammeChoiceDataQuery } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { ReactElement, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { headCells } from './ProgrammesHeadCells';
import ProgrammesTableRow from './ProgrammesTableRow';

interface ProgrammesTableProps {
  businessArea: string;
  filter;
  choicesData: ProgrammeChoiceDataQuery;
}

function ProgrammesTable({
  businessArea,
  filter,
  choicesData,
}: ProgrammesTableProps): ReactElement {
  const { t } = useTranslation();
  const { programId } = useBaseUrl();

  const initialQueryVariables = useMemo(
    () => ({
      businessAreaSlug: businessArea,
      programSlug: programId,
      search: filter.search,
      startDate: filter.startDate || null,
      endDate: filter.endDate || null,
      status: filter.status,
      sector: filter.sector,
      numberOfHouseholds: JSON.stringify({
        min: filter.numberOfHouseholdsMin,
        max: filter.numberOfHouseholdsMax,
      }),
      budget: JSON.stringify({ min: filter.budgetMin, max: filter.budgetMax }),
      dataCollectingType: filter.dataCollectingType,
    }),
    [businessArea, filter, programId],
  );

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);

  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

  const {
    data: dataPrograms,
    isLoading: isLoadingPrograms,
    error: errorPrograms,
  } = useQuery({
    queryKey: [
      'businessAreasProgramsList',
      queryVariables,
      programId,
      businessArea,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsHouseholdsList(queryVariables),
  });

  return (
    <>
      <TableWrapper>
        <UniversalRestTable
          title={t('Programmes')}
          headCells={headCells}
          queryVariables={queryVariables}
          setQueryVariables={setQueryVariables}
          data={dataPrograms}
          isLoading={isLoadingPrograms}
          error={errorPrograms}
          renderRow={(row) => (
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
