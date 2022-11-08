import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
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
import { useSurveysChoiceDataQuery } from '../../../../__generated__/graphql';
import { SurveysTable } from '../../../tables/Surveys/SurveysTable/SurveysTable';

export const SurveysPage = (): React.ReactElement => {
  const permissions = usePermissions();
  const { t } = useTranslation();
  const { data: choicesData } = useSurveysChoiceDataQuery({
    fetchPolicy: 'cache-and-network',
  });

  const [filter, setFilter] = useState({
    search: '',
    program: '',
    targetPopulation: '',
    createdBy: '',
    createdAtRange: '',
  });

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
