import FeedbackFilters from '@components/accountability/Feedback/FeedbackTable/FeedbackFilters';
import { ButtonTooltip } from '@components/core/ButtonTooltip';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import FeedbackTable from '@containers/tables/Feedback/FeedbackTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useScrollToRefOnChange } from '@hooks/useScrollToRefOnChange';
import { getFilterFromQueryParams } from '@utils/utils';
import { ReactElement, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useLocation } from 'react-router-dom';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { useProgramContext } from '../../../../programContext';

function FeedbackPage(): ReactElement {
  const { baseUrl, isAllPrograms } = useBaseUrl();
  const permissions = usePermissions();
  const { t } = useTranslation();
  const location = useLocation();
  const { isActiveProgram } = useProgramContext();

  const initialFilter = {
    feedbackId: '',
    issueType: '',
    createdBy: '',
    createdAtBefore: '',
    createdAtAfter: '',
    program: '',
    programState: isAllPrograms ? 'all' : '',
  };

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [shouldScroll, setShouldScroll] = useState(false);
  const tableRef = useRef<HTMLDivElement>(null);
  useScrollToRefOnChange(tableRef, shouldScroll, appliedFilter, () =>
    setShouldScroll(false),
  );

  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.GRIEVANCES_FEEDBACK_VIEW_LIST, permissions))
    return <PermissionDenied />;
  const canViewDetails = hasPermissions(
    PERMISSIONS.GRIEVANCES_FEEDBACK_VIEW_DETAILS,
    permissions,
  );

  return (
    <>
      <PageHeader title={t('Feedback')}>
        <ButtonTooltip
          variant="contained"
          color="primary"
          component={Link}
          to={`/${baseUrl}/grievance/feedback/create`}
          data-cy="button-submit-new-feedback"
          title={t('Programme has to be active to create a new Feedback')}
          disabled={!isActiveProgram}
        >
          {t('Submit New Feedback')}
        </ButtonTooltip>
      </PageHeader>
      <FeedbackFilters
        filter={filter}
        setFilter={setFilter}
        initialFilter={initialFilter}
        appliedFilter={appliedFilter}
        setAppliedFilter={(f) => {
          setAppliedFilter(f);
          setShouldScroll(true);
        }}
      />
      <div ref={tableRef}>
        <FeedbackTable filter={appliedFilter} canViewDetails={canViewDetails} />
      </div>
    </>
  );
}

export default withErrorBoundary(FeedbackPage, 'FeedbackPage');
