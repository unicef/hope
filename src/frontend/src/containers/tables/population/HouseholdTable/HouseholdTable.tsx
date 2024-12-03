import { TableWrapper } from '@components/core/TableWrapper';
import {
  AllHouseholdsForPopulationTableQueryVariables,
  AllHouseholdsQueryVariables,
  HouseholdChoiceDataQuery,
  HouseholdNode,
  HouseholdRdiMergeStatus,
  useAllHouseholdsForPopulationTableQuery,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { UniversalTable } from '../../UniversalTable';
import { headCells } from './HouseholdTableHeadCells';
import { HouseholdTableRow } from './HouseholdTableRow';

interface HouseholdTableProps {
  businessArea: string;
  filter;
  choicesData: HouseholdChoiceDataQuery;
  canViewDetails: boolean;
}

export function HouseholdTable({
  businessArea,
  filter,
  choicesData,
  canViewDetails,
}: HouseholdTableProps): ReactElement {
  const { t } = useTranslation();
  const { programId } = useBaseUrl();
  const matchWithdrawnValue = (): boolean | undefined => {
    if (filter.withdrawn === 'true') {
      return true;
    }
    if (filter.withdrawn === 'false') {
      return false;
    }
    return undefined;
  };

  const initialVariables: AllHouseholdsForPopulationTableQueryVariables = {
    businessArea,
    familySize: JSON.stringify({
      min: filter.householdSizeMin,
      max: filter.householdSizeMax,
    }),
    search: filter.search.trim(),
    documentType: filter.documentType,
    documentNumber: filter.documentNumber.trim(),
    admin1: filter.admin1,
    admin2: filter.admin2,
    residenceStatus: filter.residenceStatus,
    withdrawn: matchWithdrawnValue(),
    orderBy: filter.orderBy,
    program: programId,
    rdiMergeStatus: HouseholdRdiMergeStatus.Merged,
  };
  return (
    <TableWrapper>
      <UniversalTable<HouseholdNode, AllHouseholdsQueryVariables>
        title={t('Households')}
        headCells={headCells}
        rowsPerPageOptions={[10, 15, 20]}
        query={useAllHouseholdsForPopulationTableQuery}
        queriedObjectName="allHouseholds"
        initialVariables={initialVariables}
        allowSort={false}
        filterOrderBy={filter.orderBy}
        renderRow={(row) => (
          <HouseholdTableRow
            key={row.id}
            household={row}
            choicesData={choicesData}
            canViewDetails={canViewDetails}
          />
        )}
      />
    </TableWrapper>
  );
}
