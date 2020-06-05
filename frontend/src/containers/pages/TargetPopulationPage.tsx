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

  const redirectToCreate = (): void => {
    const path = `/${businessArea}/target-population/create`;
    return history.push(path);
  };

  return (
    <div>
      <PageHeader title={t('Targeting')}>
        <>
          <IconButton onClick={() => toggleInfo(true)} color="primary" aria-label="Targeting Information">
            <Info />
          </IconButton>
          <TargetingInfoDialog open={isInfoOpen} setOpen={toggleInfo}/>
          <Button
            variant='contained'
            color='primary'
            onClick={() => redirectToCreate()}
          data-cy='button-target-population-create-new'
          >
            Create new
          </Button>
        </>
      </PageHeader>
      <TargetPopulationFilters
        //targetPopulations={targetPopulations as TargetPopulationNode[]}
        filter={filter}
        onFilterChange={setFilter}
      />
      <Container>
        <TargetPopulationTable
          filter={debouncedFilter}
        />
      </Container>
    </div>
  );
}
