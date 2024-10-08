import React, { useState } from 'react';
import { PageHeader } from '@core/PageHeader';
import { useTranslation } from 'react-i18next';
import { ProgramCyclesFilters } from '@containers/tables/ProgramCyclesTablePaymentModule/ProgramCyclesFilters';
import { getFilterFromQueryParams } from '@utils/utils';
import { useLocation } from 'react-router-dom';
import { usePermissions } from '@hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { PermissionDenied } from '@core/PermissionDenied';
import { useProgramContext } from '../../../../programContext';
import { TableWrapper } from '@core/TableWrapper';
import { ProgramCyclesTablePaymentModule } from '@containers/tables/ProgramCyclesTablePaymentModule/ProgramCyclesTablePaymentModule';

const initialFilter = {
  search: '',
  status: '',
  total_entitled_quantity_usd_from: '',
  total_entitled_quantity_usd_to: '',
  start_date: '',
  end_date: '',
};

export const ProgramCyclePage = (): React.ReactElement => {
  const { t } = useTranslation();
  const permissions = usePermissions();
  const location = useLocation();
  const { selectedProgram } = useProgramContext();

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );

  if (permissions === null) return null;
  if (!selectedProgram) return null;
  if (!hasPermissions(PERMISSIONS.PM_VIEW_LIST, permissions))
    return <PermissionDenied />;

  return (
    <>
      <PageHeader title={t('Payment Module')} />
      <ProgramCyclesFilters
        filter={filter}
        setFilter={setFilter}
        initialFilter={initialFilter}
        appliedFilter={appliedFilter}
        setAppliedFilter={setAppliedFilter}
      />
      <TableWrapper>
        <ProgramCyclesTablePaymentModule
          program={selectedProgram}
          filters={appliedFilter}
        />
      </TableWrapper>
    </>
  );
};
