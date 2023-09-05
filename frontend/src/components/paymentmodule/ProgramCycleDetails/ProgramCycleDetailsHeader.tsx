import { Box, Button } from '@material-ui/core';
import { Link } from 'react-router-dom';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { BreadCrumbsItem } from '../../core/BreadCrumbs';
import { PageHeader } from '../../core/PageHeader';
import { ProgramCycleQuery } from '../../../__generated__/graphql';
import { useBaseUrl } from '../../../hooks/useBaseUrl';

interface ProgramCycleDetailsHeaderProps {
  permissions: string[];
  programCycle: ProgramCycleQuery['programCycle'];
}

export const ProgramCycleDetailsHeader = ({
  permissions,
  programCycle,
}: ProgramCycleDetailsHeaderProps): React.ReactElement => {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();
  const { name, unicefId } = programCycle;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Payment Module'),
      to: `/${baseUrl}/payment-module/`,
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
