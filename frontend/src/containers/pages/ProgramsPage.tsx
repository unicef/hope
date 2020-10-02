import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { PageHeader } from '../../components/PageHeader';
import {
  useAllProgramsQuery,
  useProgrammeChoiceDataQuery,
} from '../../__generated__/graphql';
import { CreateProgram } from '../dialogs/programs/CreateProgram';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { LoadingComponent } from '../../components/LoadingComponent';
import { ProgrammesTable } from '../tables/ProgrammesTable/ProgrammesTable';
import { useDebounce } from '../../hooks/useDebounce';
import { ProgrammesFilters } from '../tables/ProgrammesTable/ProgrammesFilter';

export function ProgramsPage(): React.ReactElement {
  const [filter, setFilter] = useState({
    search: '',
    startDate: null,
    endDate: null,
    status: [],
    sector: [],
    householdSize: {
      min: null,
      max: null,
    },
    budget: {
      min: null,
      max: null,
    },
  });
  const debouncedFilter = useDebounce(filter, 500);
  const businessArea = useBusinessArea();
  const { data, loading } = useAllProgramsQuery({
    variables: {
      businessArea,
    },
    fetchPolicy: 'cache-and-network',
  });

  const {
    data: choicesData,
    loading: choicesLoading,
  } = useProgrammeChoiceDataQuery();
  const { t } = useTranslation();

  const toolbar = (
    <PageHeader title={t('Programme Management')}>
      <CreateProgram />
    </PageHeader>
  );
  if (loading || choicesLoading) {
    return <LoadingComponent />;
  }

  return (
    <div>
      {toolbar}
      <ProgrammesFilters
        filter={filter}
        onFilterChange={setFilter}
        choicesData={choicesData}
      />
      <ProgrammesTable choicesData={choicesData} filter={debouncedFilter} />
    </div>
  );
}
