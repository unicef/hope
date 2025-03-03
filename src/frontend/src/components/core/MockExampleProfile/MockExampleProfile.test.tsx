import { expect, it } from 'vitest';
import MockExampleProfile from './MockExampleProfile';
import { waitFor, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { renderWithProviders } from 'src/testUtils/testUtils';

it('MockExampleProfile renders correctly after data is fetched', async () => {
  const { asFragment } = renderWithProviders(<MockExampleProfile />);

  // Wait for an element that indicates the data has been loaded
  await waitFor(() => {
    expect(screen.getByText(/Profile Details/i)).toBeInTheDocument();
  });

  // Take the snapshot after ensuring the data is loaded
  expect(asFragment()).toMatchSnapshot();
});
