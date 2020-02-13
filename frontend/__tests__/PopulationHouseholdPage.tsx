import React from 'react';
import { render } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import { Route } from 'react-router-dom';
import { PopulationHouseholdPage } from '../src/containers/pages/PopulationHouseholdPage';
test('Should render the Population Household Page', async () => {
  const { getByText } = render(
    <Route path='/:businessArea/population/household'>
      <PopulationHouseholdPage />
    </Route>,
    {
      route: '/afghanistan/population/household',
    },
  );
  const householdText = getByText(/Households/i);
  expect(householdText).toBeInTheDocument();
});
