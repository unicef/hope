import { Button } from '@material-ui/core';
import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  hasPermissionInModule,
  PERMISSIONS,
} from '../../../../config/permissions';
import { usePermissions } from '../../../../hooks/usePermissions';
import { PageHeader } from '../../../../components/core/PageHeader';
import { PermissionDenied } from '../../../../components/core/PermissionDenied';
import { FeedbackTable } from '../../../tables/Feedback/FeedbackTable';
import { FeedbackFilters } from '../../../../components/accountability/Feedback/FeedbackTable/FeedbackFilters';
import { getFilterFromQueryParams } from '../../../../utils/utils';
import { useBaseUrl } from '../../../../hooks/useBaseUrl';

const initialFilter = {
  feedbackId: '',
  issueType: '',
  createdBy: '',
  createdAtRangeMin: null,
  createdAtRangeMax: null,
};

export const FeedbackPage = (): React.ReactElement => {
  const { baseUrl } = useBaseUrl();
  const permissions = usePermissions();
  const { t } = useTranslation();
  const location = useLocation();

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );

  if (permissions === null) return null;
  if (
    !hasPermissionInModule(
      PERMISSIONS.ACCOUNTABILITY_FEEDBACK_VIEW_LIST,
      permissions,
    )
  )
    return <PermissionDenied />;
  const canViewDetails = hasPermissionInModule(
    PERMISSIONS.ACCOUNTABILITY_FEEDBACK_VIEW_DETAILS,
    permissions,
  );

  return (
    <>
      <PageHeader title={t('Feedback')}>
        <Button
          variant='contained'
          color='primary'
          component={Link}
          to={`/${baseUrl}/accountability/feedback/create`}
          data-cy='button-submit-new-feedback'
        >
          {t('Submit New Feedback')}
        </Button>
      </PageHeader>
      <FeedbackFilters
        filter={filter}
        setFilter={setFilter}
        initialFilter={initialFilter}
        appliedFilter={appliedFilter}
        setAppliedFilter={setAppliedFilter}
      />
      <FeedbackTable filter={appliedFilter} canViewDetails={canViewDetails} />
    </>
  );
};
