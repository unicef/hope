import { expect, it } from 'vitest';
import MockExampleProfile from './MockExampleProfile'; // Adjust the import path as needed
import { renderWithProviders } from '../../../testUtils/testUtils';
import { waitFor, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

it('MockExampleProfile renders correctly after data is fetched', async () => {
  const { asFragment } = renderWithProviders(<MockExampleProfile />);

  // Wait for an element that indicates the data has been loaded
  await waitFor(() => {
    expect(screen.getByText(/Profile Details/i)).toBeInTheDocument();
  });

  // Take the snapshot after ensuring the data is loaded
  expect(asFragment()).toMatchSnapshot();
});
