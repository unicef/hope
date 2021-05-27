import React, {useState} from 'react';
import {PageHeader} from '../../components/PageHeader';
import {useBusinessArea} from '../../hooks/useBusinessArea';
import {useDebounce} from '../../hooks/useDebounce';
import {ReportingFilters} from '../tables/ReportingTable/ReportingFilters';
import {ReportingTable} from '../tables/ReportingTable/ReportingTable';
import {NewReportForm} from '../../components/Reporting/NewReportForm';
import {usePermissions} from '../../hooks/usePermissions';
import {hasPermissions, PERMISSIONS} from '../../config/permissions';
import {useReportChoiceDataQuery} from '../../__generated__/graphql';
import {LoadingComponent} from '../../components/LoadingComponent';
import {PermissionDenied} from '../../components/PermissionDenied';

export const ReportingPage = (): React.ReactElement => {
  const businessArea = useBusinessArea();
  const permissions = usePermissions();

  const {
    data: choicesData,
    loading: choicesLoading,
  } = useReportChoiceDataQuery();

  const [filter, setFilter] = useState({
    type: '',
    createdFrom: undefined,
    createdTo: undefined,
    status: '',
    onlyMy: false,
  });
  const debouncedFilter = useDebounce(filter, 500);
  if (choicesLoading) return <LoadingComponent />;

  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.REPORTING_EXPORT, permissions))
    return <PermissionDenied />;

  return (
    <>
      <PageHeader title='Reporting'>
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
      />
    </>
  );
};
