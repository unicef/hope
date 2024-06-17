import { Box, Button } from '@material-ui/core';
import { Link } from 'react-router-dom';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { BreadCrumbsItem } from '../../core/BreadCrumbs';
import { PageHeader } from '../../core/PageHeader';
import {
  ProgramCycleQuery,
  useProgramQuery,
} from '../../../__generated__/graphql';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { LoadingComponent } from '../../core/LoadingComponent';

interface ProgramCycleDetailsHeaderProgramDetailsProps {
  permissions: string[];
  programCycle: ProgramCycleQuery['programCycle'];
}

export const ProgramCycleDetailsHeaderProgramDetails = ({
  permissions,
  programCycle,
}: ProgramCycleDetailsHeaderProgramDetailsProps): React.ReactElement => {
  const { t } = useTranslation();
  const { baseUrl, programId } = useBaseUrl();
  const { name, unicefId } = programCycle;
  const { data, loading } = useProgramQuery({
    variables: {
      id: programId,
    },
  });
  if (!data) return null;
  if (loading) return <LoadingComponent />;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: `Programme: ${data.program.name}`,
      to: `/${baseUrl}/details/${data.program.id}/`,
    },
  ];
  //TODO: rename PM_CREATE permissions to PM_CREATE_PAYMENT_PLAN and so on
  //TODO: change routing for payment plans
  return (
    <PageHeader
      title={`${name} (ID: ${unicefId})`}
      breadCrumbs={
        hasPermissions(PERMISSIONS.PM_PROGRAMME_CYCLE_VIEW_LIST, permissions)
          ? breadCrumbsItems
          : null
      }
    >
      <Box display='flex' mt={2} mb={2}>
        {hasPermissions(PERMISSIONS.PM_CREATE, permissions) && (
          <Button
            variant='contained'
            color='primary'
            component={Link}
            to={`/${baseUrl}/payment-module/new-plan`}
            data-cy='button-create-payment-plan'
          >
            {t('Create Payment Plan')}
          </Button>
        )}
      </Box>
    </PageHeader>
  );
};
