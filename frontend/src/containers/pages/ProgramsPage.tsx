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
  if (choicesLoading) {
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
      <ProgrammesTable
        businessArea={businessArea}
        choicesData={choicesData}
        filter={debouncedFilter}
      />
    </div>
  );
}
