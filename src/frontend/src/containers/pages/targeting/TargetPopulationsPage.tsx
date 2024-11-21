import { IconButton } from '@mui/material';
import { Info } from '@mui/icons-material';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { TargetPopulationTableFilters } from '@components/targeting/TargetPopulationTableFilters';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { usePermissions } from '@hooks/usePermissions';
import { getFilterFromQueryParams } from '@utils/utils';
import { TargetingInfoDialog } from '../../dialogs/targetPopulation/TargetingInfoDialog';
import { TargetPopulationTable } from '../../tables/targeting/TargetPopulationTable';
import { CreateTPMenu } from '@components/targeting/CreateTPMenu';
import { useProgramQuery } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { TargetPopulationForPeopleTable } from '@containers/tables/targeting/TargetPopulationForPeopleTable';
import { TargetPopulationForPeopleFilters } from '@components/targeting/TargetPopulationForPeopleFilters';
import { UniversalErrorBoundary } from '@components/core/UniversalErrorBoundary';

const initialFilter = {
  name: '',
  status: '',
  totalHouseholdsCountMin: '',
  totalHouseholdsCountMax: '',
  createdAtRangeMin: '',
  createdAtRangeMax: '',
};

export const TargetPopulationsPage = (): ReactElement => {
  const location = useLocation();
  const { t } = useTranslation();
  const permissions = usePermissions();
  const { programId } = useBaseUrl();

  const { data: programData } = useProgramQuery({
    variables: { id: programId },
  });
  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [isInfoOpen, setToggleInfo] = useState(false);

  const canCreate = hasPermissions(PERMISSIONS.TARGETING_CREATE, permissions);

  if (!programData || !permissions) return null;
  if (!hasPermissions(PERMISSIONS.TARGETING_VIEW_LIST, permissions))
    return <PermissionDenied />;
  let Table = TargetPopulationTable;
  let Filters = TargetPopulationTableFilters;
  if (programData.program.isSocialWorkerProgram) {
    Table = TargetPopulationForPeopleTable;
    Filters = TargetPopulationForPeopleFilters;
  }

  return (
    <UniversalErrorBoundary
      location={location}
      beforeCapture={(scope) => {
        scope.setTag('location', location.pathname);
        scope.setTag('component', 'TargetPopulationsPage.tsx');
      }}
      componentName="TargetPopulationsPage"
    >
      <>
        <PageHeader title={t('Targeting')}>
          <>
            <IconButton
              onClick={() => setToggleInfo(true)}
              color="primary"
              aria-label="Targeting Information"
              data-cy="button-target-population-info"
            >
              <Info />
            </IconButton>
            <TargetingInfoDialog open={isInfoOpen} setOpen={setToggleInfo} />
            {canCreate && <CreateTPMenu />}
          </>
        </PageHeader>
        <Filters
          filter={filter}
          setFilter={setFilter}
          initialFilter={initialFilter}
          appliedFilter={appliedFilter}
          setAppliedFilter={setAppliedFilter}
        />
        <Table
          filter={appliedFilter}
          canViewDetails={hasPermissions(
            PERMISSIONS.TARGETING_VIEW_DETAILS,
            permissions,
          )}
        />
      </>
    </UniversalErrorBoundary>
  );
};
