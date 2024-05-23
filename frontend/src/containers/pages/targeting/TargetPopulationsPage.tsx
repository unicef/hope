import { IconButton } from '@mui/material';
import { Info } from '@mui/icons-material';
import * as React from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { TargetPopulationFilters } from '@components/targeting/TargetPopulationFilters';
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

const initialFilter = {
  name: '',
  status: '',
  totalHouseholdsCountMin: '',
  totalHouseholdsCountMax: '',
  createdAtRangeMin: '',
  createdAtRangeMax: '',
};

export const TargetPopulationsPage = (): React.ReactElement => {
  const location = useLocation();
  const { t } = useTranslation();
  const permissions = usePermissions();
  const {  programId } = useBaseUrl();
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

  if (permissions === null) return null;

  const canCreate = hasPermissions(PERMISSIONS.TARGETING_CREATE, permissions);

  if (!hasPermissions(PERMISSIONS.TARGETING_VIEW_LIST, permissions))
    return <PermissionDenied />;
  if (!programData) return null;
  let Table = TargetPopulationTable;
  let Filters = TargetPopulationFilters;
  if (programData.program.isSocialWorkerProgram) {
    Table = TargetPopulationForPeopleTable;
    Filters = TargetPopulationForPeopleFilters;
  }
  return (
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
  );
};
