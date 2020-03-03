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
  const [sexFilter, setSexFilter] = useState('none');
  const [textFilter, setTextFilter] = useState();

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Population',
      to: `/${businessArea}/population/household`,
    },
  ];

  const handleMinAgeFilter = (value: number): void => {
    setAgeFilter({ ...ageFilter, min: value });
  };
  const handleMaxAgeFilter = (value: number): void => {
    setAgeFilter({ ...ageFilter, max: value });
  };
  const handleTextFilter = (value: string): void => {
    setTextFilter(value);
  };
  const handleSexFilter = (value: string): void => {
    setSexFilter(value);
  };
  return (
    <>
      <PageHeader title='Individuals' breadCrumbs={breadCrumbsItems} />
      <IndividualsFilter
        sexFilter={sexFilter}
        individualSexFilter={handleSexFilter}
        individualMaxAgeFilter={handleMaxAgeFilter}
        individualMinAgeFilter={handleMinAgeFilter}
        individualTextFilter={handleTextFilter}
      />
      <Container>
        <IndividualsListTable
          textFilter={textFilter}
          sexFilter={sexFilter}
          ageFilter={ageFilter}
          businessArea={businessArea}
        />
      </Container>
    </>
  );
}
