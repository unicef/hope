import React, { useState } from 'react';
import styled from 'styled-components';
import { PageHeader } from '../../components/PageHeader';
import { IndividualsListTable } from '../tables/IndividualsListTable';
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
      title: 'Population',
      to: `/${businessArea}/`,
    },
  ];

  const handleMinAgeFilter = (value: number): void => {
    setAgeFilter({ ...ageFilter, min: value });
  };
  const handleMaxAgeFilter = (value: number): void => {
    setAgeFilter({ ...ageFilter, max: value });
  };
  const handleTextFilter = (value: string): string => {
    return value;
  };
  const handleSexFilter = (value: string): string => {
    return value;
  };
  return (
    <>
      <PageHeader title='Individuals' breadCrumbs={breadCrumbsItems} />
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
