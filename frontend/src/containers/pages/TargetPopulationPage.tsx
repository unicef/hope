import React, { useState } from 'react';
import { useHistory } from 'react-router-dom';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { Button } from '@material-ui/core';
import { useDebounce } from '../../hooks/useDebounce';
import { PageHeader } from '../../components/PageHeader';
import { TargetPopulationFilters } from '../../components/TargetPopulation/TargetPopulationFilters';
import { TargetPopulationTable } from '../tables/TargetPopulationTable';
import { useBusinessArea } from '../../hooks/useBusinessArea';

const Container = styled.div`
  && {
    display: flex;
    flex-direction: column;
    min-width: 100%;
  }
`;

export function TargetPopulationPage() {
  const { t } = useTranslation();
  const history = useHistory();
  const businessArea = useBusinessArea();
  const [filter, setFilter] = useState({
    numIndividuals: {
      min: undefined,
      max: undefined,
    },
    name: '',
  })
  const debouncedFilter = useDebounce(filter, 500);

  const redirectToCreate = () => {
    const path = `/${businessArea}/target-population/create`;
    return history.push(path);
  };

  return (
    <div>
      <PageHeader title={t('Targeting')}>
        <Button
          variant='contained'
          color='primary'
          onClick={() => redirectToCreate()}
        >
          Create new
        </Button>
      </PageHeader>
      <TargetPopulationFilters
        //targetPopulations={targetPopulations as TargetPopulationNode[]}
        filter={filter}
        onFilterChange={setFilter}
      />
      <Container>
        <TargetPopulationTable
          filter={debouncedFilter}
          businessArea={businessArea}
        />
      </Container>
    </div>
  );
}
