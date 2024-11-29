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
import { adjustHeadCells } from '@utils/utils';
import { ReactElement } from 'react';
import { useProgramContext } from 'src/programContext';
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
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
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
  const replacements = {
    unicefId: (_beneficiaryGroup) => `${_beneficiaryGroup?.groupLabel} ID`,
    head_of_household__full_name: (_beneficiaryGroup) =>
      `Head of ${_beneficiaryGroup?.groupLabel}`,
    size: (_beneficiaryGroup) => `${_beneficiaryGroup?.groupLabel} Size`,
  };

  const adjustedHeadCells = adjustHeadCells(
    headCells,
    beneficiaryGroup,
    replacements,
  );

  return (
    <TableWrapper>
      <UniversalTable<HouseholdNode, AllHouseholdsQueryVariables>
        title={`${beneficiaryGroup?.groupLabelPlural}`}
        headCells={adjustedHeadCells}
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
