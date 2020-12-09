import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { PageHeader } from '../../components/PageHeader';
import { useProgrammeChoiceDataQuery } from '../../__generated__/graphql';
import { CreateProgram } from '../dialogs/programs/CreateProgram';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { LoadingComponent } from '../../components/LoadingComponent';
import { ProgrammesTable } from '../tables/ProgrammesTable/ProgrammesTable';
import { useDebounce } from '../../hooks/useDebounce';
import { ProgrammesFilters } from '../tables/ProgrammesTable/ProgrammesFilter';
import { usePermissions } from '../../hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from '../../config/permissions';
import { PermissionDenied } from '../../components/PermissionDenied';

export function ProgramsPage(): React.ReactElement {
  const [filter, setFilter] = useState({
    startDate: undefined,
    endDate: undefined,
    status: [],
    sector: [],
    numberOfHouseholds: {
      min: undefined,
      max: undefined,
    },
    budget: {
      min: undefined,
      max: undefined,
    },
  });
  const debouncedFilter = useDebounce(filter, 500);
  const businessArea = useBusinessArea();
  const permissions = usePermissions();

  const {
    data: choicesData,
    loading: choicesLoading,
  } = useProgrammeChoiceDataQuery();
  const { t } = useTranslation();

  if (choicesLoading) return <LoadingComponent />;

  if (permissions === null) return null;

  const canViewListAndDetails = hasPermissions(
    PERMISSIONS.PRORGRAMME_VIEW_LIST_AND_DETAILS,
    permissions,
  );
  const canCreate = hasPermissions(PERMISSIONS.PROGRAMME_CREATE, permissions);

  if (!canViewListAndDetails && !canCreate) return <PermissionDenied />;

  const toolbar = (
    <PageHeader title={t('Programme Management')}>
      <CreateProgram />
    </PageHeader>
  );

  return (
    <div>
      {canCreate && toolbar}
      {canViewListAndDetails && (
        <>
          <ProgrammesFilters
            filter={filter}
            onFilterChange={setFilter}
            choicesData={choicesData}
          />
          <ProgrammesTable
            businessArea={businessArea}
            choicesData={choicesData}
            filter={debouncedFilter}
          />
        </>
      )}
    </div>
  );
}
