import { Box } from '@material-ui/core';
import React from 'react';
import { useParams } from 'react-router-dom';
import {
  useProgrammeChoiceDataQuery,
  useProgramQuery,
} from '../../../__generated__/graphql';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { TableWrapper } from '../../../components/core/TableWrapper';
import { ProgramCyclesActionsTable } from '../../tables/programs/ProgramCyclesActionsTable';
import { ProgramDetails } from '../../../components/programs/ProgramDetails/ProgramDetails';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { usePermissions } from '../../../hooks/usePermissions';
import { isPermissionDeniedError } from '../../../utils/utils';
import { UniversalActivityLogTable } from '../../tables/UniversalActivityLogTable';
import { ProgramDetailsPageHeader } from '../headers/ProgramDetailsPageHeader';

export const ProgramDetailsPage = (): React.ReactElement => {
  const { id } = useParams();
  const { data, loading, error } = useProgramQuery({
    variables: { id },
    fetchPolicy: 'cache-and-network',
  });
  const {
    data: choices,
    loading: choicesLoading,
  } = useProgrammeChoiceDataQuery();
  const permissions = usePermissions();

  if (loading || choicesLoading) return <LoadingComponent />;

  if (isPermissionDeniedError(error)) return <PermissionDenied />;

  if (!data?.program || !choices || permissions === null) return null;

  const { program } = data;
  return (
    <div>
      <ProgramDetailsPageHeader
        program={program}
        canActivate={hasPermissions(
          PERMISSIONS.PROGRAMME_ACTIVATE,
          permissions,
        )}
        canEdit={hasPermissions(PERMISSIONS.PROGRAMME_UPDATE, permissions)}
        canRemove={hasPermissions(PERMISSIONS.PROGRAMME_REMOVE, permissions)}
        canFinish={hasPermissions(PERMISSIONS.PROGRAMME_FINISH, permissions)}
        canDuplicate={hasPermissions(
          PERMISSIONS.PROGRAMME_DUPLICATE,
          permissions,
        )}
      />
      <Box display='flex' flexDirection='column'>
        <ProgramDetails program={program} choices={choices} />
        <TableWrapper>
          <ProgramCyclesActionsTable program={program} />
        </TableWrapper>
        {hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions) && (
          <UniversalActivityLogTable objectId={program.id} />
        )}
      </Box>
    </div>
  );
};
