import React, { useState } from 'react';
import styled from 'styled-components';
import { PageHeader } from '../../components/PageHeader';
import { IndividualsListTable } from '../IndividualsListTable';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { IndividualsFilter } from '../../components/population/IndividualsFilter';
import { BreadCrumbsItem } from '../../components/BreadCrumbs';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
`;

export function PopulationIndividualsPage(): React.ReactElement {
  const businessArea = useBusinessArea();
  const [ageFilter, setAgeFilter] = useState({ min: null, max: null });

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Individuals',
      to: `/${businessArea}/`,
    },
  ];

  const handleMinAgeFilter = (event): void => {
    setAgeFilter({ ...ageFilter, min: event.target.value });
  };
  const handleMaxAgeFilter = (event): void => {
    setAgeFilter({ ...ageFilter, max: event.target.value });
  };
  const handleTextFilter = (event): string => {
    return event.target.value;
  };
  const handleSexFilter = (event): string => {
    return event.target.value;
  };
  return (
    <>
      <PageHeader title='Individuals' />
      <IndividualsFilter
        individualSexFilter={handleSexFilter}
        individualMaxAgeFilter={handleMaxAgeFilter}
        individualMinAgeFilter={handleMinAgeFilter}
        individualTextFilter={handleTextFilter}
      />
      <Container>
        <IndividualsListTable
          ageFilter={ageFilter}
          businessArea={businessArea}
        />
      </Container>
    </>
  );
}
