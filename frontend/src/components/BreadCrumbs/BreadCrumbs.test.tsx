import React from 'react';
import { render, fireEvent, wait } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { BreadCrumbsElement } from './BreadCrumbs';

const breadCrumbData = {
  title: 'Sample',
  to: '/test'
}

describe('Breadcrumbs Element', () => {
  test('Breadcrumb element renders with sample text', () => {
    const { container } = render(
      <MemoryRouter>
        <BreadCrumbsElement title={breadCrumbData.title} to={breadCrumbData.to} last={false} />
      </MemoryRouter>
    )
    expect(container).toHaveTextContent(breadCrumbData.title);
  })
  test('Breadcrumb element has given link', () => {
    const { container } = render(
      <MemoryRouter>
        <BreadCrumbsElement title={breadCrumbData.title} to={breadCrumbData.to} last={false} />
      </MemoryRouter>
    )
    const link = document.querySelector('a')
    expect(link.getAttribute('href')).toEqual(breadCrumbData.to);
  })
})