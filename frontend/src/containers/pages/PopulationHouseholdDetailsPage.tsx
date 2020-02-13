import React from 'react';
import { useParams } from 'react-router-dom';
import { HouseholdDetails } from '../../components/population/HouseholdDetails';
import { PageHeader } from '../../components/PageHeader';
import { useHouseholdQuery, HouseholdNode } from '../../__generated__/graphql';
import { BreadCrumbsItem } from '../../components/BreadCrumbs';
import { useBusinessArea } from '../../hooks/useBusinessArea';

export function PopulationHouseholdDetailsPage(): React.ReactElement {
  const { id } = useParams();
  const businessArea = useBusinessArea();
  const { data, loading } = useHouseholdQuery({
    variables: { id },
  });

  if (loading) return null;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Household Details',
      to: `/${businessArea}/population/household`,
    },
  ];

  return (
    <div>
      <PageHeader
        title={`Household ID: ${id}`}
        breadCrumbs={breadCrumbsItems}
      />
      <HouseholdDetails houseHold={data.household as HouseholdNode} />
    </div>
  );
}
