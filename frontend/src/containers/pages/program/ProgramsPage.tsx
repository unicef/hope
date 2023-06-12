import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { PageHeader } from '../../../components/core/PageHeader';
import { useProgrammeChoiceDataQuery } from '../../../__generated__/graphql';
import { CreateProgram } from '../../dialogs/programs/CreateProgram';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { ProgrammesTable } from '../../tables/ProgrammesTable/ProgrammesTable';
import { ProgrammesFilters } from '../../tables/ProgrammesTable/ProgrammesFilter';
import { usePermissions } from '../../../hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { getFilterFromQueryParams } from '../../../utils/utils';

const initialFilter = {
  search: '',
  startDate: undefined,
  endDate: undefined,
  status: '',
  sector: [],
  numberOfHouseholdsMin: '',
  numberOfHouseholdsMax: '',
  budgetMin: '',
  budgetMax: '',
};

export const ProgramsPage = (): React.ReactElement => {
  const location = useLocation();

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const businessArea = useBusinessArea();
  const permissions = usePermissions();

  const {
    data: choicesData,
    loading: choicesLoading,
  } = useProgrammeChoiceDataQuery();
  const { t } = useTranslation();

  if (choicesLoading) return <LoadingComponent />;

  if (permissions === null || !choicesData) return null;

  if (
    !hasPermissions(PERMISSIONS.PRORGRAMME_VIEW_LIST_AND_DETAILS, permissions)
  )
    return <PermissionDenied />;

  const toolbar = (
    <PageHeader title={t('Programme Management')}>
      <CreateProgram />
    </PageHeader>
  );

  return (
    <div>
      {hasPermissions(PERMISSIONS.PROGRAMME_CREATE, permissions) && toolbar}
      <ProgrammesFilters
        filter={filter}
        choicesData={choicesData}
        setFilter={setFilter}
        initialFilter={initialFilter}
        appliedFilter={appliedFilter}
        setAppliedFilter={setAppliedFilter}
      />
      <ProgrammesTable
        businessArea={businessArea}
        choicesData={choicesData}
        filter={appliedFilter}
      />
    </div>
  );
};
