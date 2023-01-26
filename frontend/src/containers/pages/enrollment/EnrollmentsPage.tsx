import { Button, IconButton } from '@material-ui/core';
import { Info } from '@material-ui/icons';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { EnrollmentsTable } from '../../../components/enrollment/EnrollmentsTable';
import { EnrollmentsFilters } from '../../../components/enrollment/EnrollmentsTable/EnrollmentsFilters';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useDebounce } from '../../../hooks/useDebounce';
import { usePermissions } from '../../../hooks/usePermissions';

export const EnrollmentsPage = (): React.ReactElement => {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();
  const [filter, setFilter] = useState({
    name: '',
    status: '',
    size: {
      min: undefined,
      max: undefined,
    },
    numIndividuals: {
      min: undefined,
      max: undefined,
    },
  });
  const [isInfoOpen, setToggleInfo] = useState(false);
  const debouncedFilter = useDebounce(filter, 500);

  if (permissions === null) return null;

  const canCreate = hasPermissions(PERMISSIONS.ENROLLMENT_CREATE, permissions);

  if (!hasPermissions(PERMISSIONS.ENROLLMENT_VIEW_LIST, permissions))
    return <PermissionDenied />;

  return (
    <>
      <PageHeader title={t('Enrollment')}>
        <>
          <IconButton
            onClick={() => setToggleInfo(true)}
            color='primary'
            aria-label='Targeting Information'
          >
            <Info />
          </IconButton>
          {/* <TargetingInfoDialog open={isInfoOpen} setOpen={setToggleInfo} /> */}
          {canCreate && (
            <Button
              variant='contained'
              color='primary'
              component={Link}
              to={`/${businessArea}/enrollment/create`}
              data-cy='button-enrollment-create-new'
            >
              Create new
            </Button>
          )}
        </>
      </PageHeader>
      <EnrollmentsFilters filter={filter} onFilterChange={setFilter} />
      <EnrollmentsTable
        filter={debouncedFilter}
        canViewDetails={hasPermissions(
          PERMISSIONS.ENROLLMENT_VIEW_DETAILS,
          permissions,
        )}
      />
    </>
  );
};
