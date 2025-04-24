import { TableWrapper } from '@components/core/TableWrapper';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { PaginatedTPHouseholdListList } from '@restgenerated/models/PaginatedTPHouseholdListList';
import { TPHouseholdList } from '@restgenerated/models/TPHouseholdList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { headCells } from './TargetPopulationPeopleHeadCells';
import { TargetPopulationPeopleTableRow } from './TargetPopulationPeopleRow';

interface TargetPopulationPeopleTableProps {
  id?: string;
  variables?;
  canViewDetails?: boolean;
}

export function TargetPopulationPeopleTable({
  id,
  variables,
  canViewDetails,
}: TargetPopulationPeopleTableProps): ReactElement {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const initialQueryVariables = {
    businessArea,
    ...variables,
  };
  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);

  const {
    data: householdsData,
    isLoading,
    error,
  } = useQuery<PaginatedTPHouseholdListList>({
    queryKey: [
      'businessAreasProgramsPaymentPlansPaymentsList',
      businessArea,
      programId,
      queryVariables,
      id,
    ],
    queryFn: () => {
      return RestService.restBusinessAreasProgramsTargetPopulationsHouseholdsList(
        {
          businessAreaSlug: businessArea,
          programSlug: programId,
          targetPopulationId: id,
          ...queryVariables,
        },
      );
    },
  });

  return (
    <TableWrapper>
      <UniversalRestTable
        title={t('People')}
        headCells={headCells}
        rowsPerPageOptions={[10, 15, 20]}
        isLoading={isLoading}
        error={error}
        queryVariables={queryVariables}
        setQueryVariables={setQueryVariables}
        data={householdsData}
        renderRow={(row: TPHouseholdList) => (
          <TargetPopulationPeopleTableRow
            key={row.id}
            payment={row}
            canViewDetails={canViewDetails}
          />
        )}
      />
    </TableWrapper>
  );
}
