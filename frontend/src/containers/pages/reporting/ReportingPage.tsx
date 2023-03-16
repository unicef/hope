import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { NewReportForm } from '../../../components/reporting/NewReportForm';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useDebounce } from '../../../hooks/useDebounce';
import { usePermissions } from '../../../hooks/usePermissions';
import { getFilterFromQueryParams } from '../../../utils/utils';
import {
  useMeQuery,
  useReportChoiceDataQuery,
} from '../../../__generated__/graphql';
import { ReportingFilters } from '../../tables/ReportingTable/ReportingFilters';
import { ReportingTable } from '../../tables/ReportingTable/ReportingTable';

const initialFilter = {
  type: '',
  createdFrom: undefined,
  createdTo: undefined,
  status: '',
  onlyMy: false,
};

export const ReportingPage = (): React.ReactElement => {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();
  const location = useLocation();

  const {
    data: choicesData,
    loading: choicesLoading,
  } = useReportChoiceDataQuery();

  const { data: meData, loading: meLoading } = useMeQuery({
    fetchPolicy: 'cache-first',
  });

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );

  const debouncedFilter = useDebounce(filter, 500);
  if (choicesLoading || meLoading) return <LoadingComponent />;

  if (!choicesData || !meData || permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.REPORTING_EXPORT, permissions))
    return <PermissionDenied />;

  return (
    <>
      <PageHeader title={t('Reporting')}>
        <NewReportForm />
      </PageHeader>
      <ReportingFilters
        filter={filter}
        onFilterChange={setFilter}
        choicesData={choicesData}
      />
      <ReportingTable
        filter={debouncedFilter}
        businessArea={businessArea}
        choicesData={choicesData}
        meData={meData}
      />
    </>
  );
};
