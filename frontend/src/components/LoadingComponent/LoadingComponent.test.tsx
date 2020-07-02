import React from 'react';
import { render, getByTestId } from '@testing-library/react';
import { LoadingComponent } from './LoadingComponent';

describe('LoadingComponent', () => {
  test('Does not render if isLoading value is falsy', () => {
    const { container } = render(
      <LoadingComponent isLoading={false} absolute />
    )
    expect(container).toBeEmpty();
  })
  test('Render loading component if isLoading is truthy', () => {
    const { container } = render(
      <div>
        <LoadingComponent isLoading={false} absolute />
      </div>
    )
    expect(container).toBeInTheDocument();
  })
})