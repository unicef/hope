import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { CreateSurveyMenu } from '../../../../components/accountability/Surveys/CreateSurveyMenu';
import { SurveysFilters } from '../../../../components/accountability/Surveys/SurveysTable/SurveysFilters';
import { PageHeader } from '../../../../components/core/PageHeader';
import { PermissionDenied } from '../../../../components/core/PermissionDenied';
import {
  hasPermissionInModule,
  PERMISSIONS,
} from '../../../../config/permissions';
import { useDebounce } from '../../../../hooks/useDebounce';
import { usePermissions } from '../../../../hooks/usePermissions';
import { getFilterFromQueryParams } from '../../../../utils/utils';
import { useSurveysChoiceDataQuery } from '../../../../__generated__/graphql';
import { SurveysTable } from '../../../tables/Surveys/SurveysTable/SurveysTable';

const initialFilter = {
  search: '',
  program: '',
  targetPopulation: '',
  createdBy: '',
  createdAtRangeMin: null,
  createdAtRangeMax: null,
};

export const SurveysPage = (): React.ReactElement => {
  const permissions = usePermissions();
  const { t } = useTranslation();
  const { data: choicesData } = useSurveysChoiceDataQuery({
    fetchPolicy: 'cache-and-network',
  });
  const location = useLocation();

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );

  const debouncedFilter = useDebounce(filter, 500);

  if (!choicesData || permissions === null) return null;
  if (
    !hasPermissionInModule(
      PERMISSIONS.ACCOUNTABILITY_SURVEY_VIEW_LIST,
      permissions,
    )
  )
    return <PermissionDenied />;
  const canViewDetails = hasPermissionInModule(
    PERMISSIONS.ACCOUNTABILITY_SURVEY_VIEW_DETAILS,
    permissions,
  );

  return (
    <>
      <PageHeader title={t('Surveys')}>
        <CreateSurveyMenu />
      </PageHeader>
      <SurveysFilters filter={filter} onFilterChange={setFilter} />
      <SurveysTable
        filter={debouncedFilter}
        canViewDetails={canViewDetails}
        choicesData={choicesData}
      />
    </>
  );
};
