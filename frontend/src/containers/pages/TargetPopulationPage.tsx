import React, { useState } from 'react';
import { useHistory } from 'react-router-dom';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { Button, IconButton } from '@material-ui/core';
import { Info } from '@material-ui/icons';
import { useDebounce } from '../../hooks/useDebounce';
import { PageHeader } from '../../components/PageHeader';
import { TargetPopulationFilters } from '../../components/TargetPopulation/TargetPopulationFilters';
import { TargetPopulationTable } from '../tables/TargetPopulationTable';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { TargetingInfoDialog } from '../dialogs/targetPopulation/TargetingInfoDialog';
import { ProgramNode, useAllProgramsQuery } from '../../__generated__/graphql';
import { LoadingComponent } from '../../components/LoadingComponent';
import { usePermissions } from '../../hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from '../../config/permissions';
import { PermissionDenied } from '../../components/PermissionDenied';

const Container = styled.div`
  && {
    display: flex;
    flex-direction: column;
    min-width: 100%;
  }
`;

export function TargetPopulationPage(): React.ReactElement {
  const { t } = useTranslation();
  const history = useHistory();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();
  const [filter, setFilter] = useState({
    numIndividuals: {
      min: undefined,
      max: undefined,
    },
    name: '',
    status: '',
  });
  const [isInfoOpen, toggleInfo] = useState(false);
  const debouncedFilter = useDebounce(filter, 500);
  const { data, loading } = useAllProgramsQuery({
    variables: { businessArea },
  });

  if (loading) return <LoadingComponent />;
  if (permissions === null) return null;

  const canViewList = hasPermissions(
    PERMISSIONS.TARGETING_VIEW_LIST,
    permissions,
  );
  const canCreate = hasPermissions(PERMISSIONS.TARGETING_CREATE, permissions);

  if (!canViewList && !canCreate) return <PermissionDenied />;
  if (!data) return null;

  const { allPrograms } = data;
  const programs = allPrograms.edges.map((edge) => edge.node);

  const redirectToCreate = (): void => {
    const path = `/${businessArea}/target-population/create`;
    return history.push(path);
  };

  return (
    <div>
      <PageHeader title={t('Targeting')}>
        <>
          <IconButton
            onClick={() => toggleInfo(true)}
            color='primary'
            aria-label='Targeting Information'
          >
            <Info />
          </IconButton>
          <TargetingInfoDialog open={isInfoOpen} setOpen={toggleInfo} />
          {canCreate && (
            <Button
              variant='contained'
              color='primary'
              onClick={() => redirectToCreate()}
              data-cy='button-target-population-create-new'
            >
              Create new
            </Button>
          )}
        </>
      </PageHeader>
      {canViewList && (
        <>
          <TargetPopulationFilters
            //targetPopulations={targetPopulations as TargetPopulationNode[]}
            filter={filter}
            programs={programs as ProgramNode[]}
            onFilterChange={setFilter}
          />
          <Container>
            <TargetPopulationTable
              filter={debouncedFilter}
              canViewDetails={hasPermissions(
                PERMISSIONS.TARGETING_VIEW_DETAILS,
                permissions,
              )}
            />
          </Container>
        </>
      )}
    </div>
  );
}
