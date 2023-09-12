import React from 'react';
import { useTranslation } from 'react-i18next';
import {
  AllProgramCyclesQuery,
  AllProgramCyclesQueryVariables,
  useAllProgramCyclesQuery,
  useProgrammeChoiceDataQuery,
} from '../../../../../__generated__/graphql';
import { LoadingComponent } from '../../../../../components/core/LoadingComponent';
import { TableWrapper } from '../../../../../components/core/TableWrapper';
import { PERMISSIONS, hasPermissions } from '../../../../../config/permissions';
import { usePermissions } from '../../../../../hooks/usePermissions';
import { choicesToDict } from '../../../../../utils/utils';
import { UniversalTable } from '../../../UniversalTable';
import { headCells } from './ProgramCyclesTableHeadCells';
import { ProgramCyclesTableRow } from './ProgramCyclesTableRow';

interface ProgramCyclesTableProps {
  filter;
}

export const ProgramCyclesTable = ({
  filter,
}: ProgramCyclesTableProps): React.ReactElement => {
  const { data: programChoiceData, loading } = useProgrammeChoiceDataQuery();
  const { t } = useTranslation();

  const initialVariables: AllProgramCyclesQueryVariables = {
    search: filter.search,
    status: filter.status,
    startDate: filter.startDate,
    endDate: filter.endDate,
  };

  const permissions = usePermissions();

  if (!permissions) {
    return null;
  }

  if (loading) {
    return <LoadingComponent />;
  }

  const statusChoices: {
    [id: number]: string;
  } = choicesToDict(programChoiceData.programCycleStatusChoices);

  const canViewProgramCycleDetails = hasPermissions(
    PERMISSIONS.PM_PROGRAMME_CYCLE_VIEW_DETAILS,
    permissions,
  );

  return (
    <TableWrapper>
      <UniversalTable<
        AllProgramCyclesQuery['allProgramCycles']['edges'][number]['node'],
        AllProgramCyclesQueryVariables
      >
        headCells={headCells}
        title={t('Programme Cycles')}
        rowsPerPageOptions={[10, 15, 20, 40]}
        query={useAllProgramCyclesQuery}
        queriedObjectName='allProgramCycles'
        initialVariables={initialVariables}
        defaultOrderBy='created_at'
        defaultOrderDirection='desc'
        renderRow={(row) => (
          <ProgramCyclesTableRow
            key={row.id}
            programCycle={row}
            statusChoices={statusChoices}
            canViewProgramCycleDetails={canViewProgramCycleDetails}
          />
        )}
      />
    </TableWrapper>
  );
};
