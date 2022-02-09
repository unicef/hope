import React from 'react';
import { mockedIndividual } from '../../../../jest/mocks';
import { renderWithRouter } from '../../../../jest/setupTests';
import { IndividualNode } from '../../../__generated__/graphql';
import { IndividualsBioData } from '../IndividualBioData';

describe('components/IndividualBioData', () => {
  jest.mock('react-i18next');

  const defaultProps = {
    individual: mockedIndividual as IndividualNode,
  };
  const initializeComponent = () =>
    renderWithRouter(
      <IndividualsBioData individual={defaultProps.individual} />,
    );

  it('should render', () => {
    const { container } = initializeComponent();
    expect(container).toMatchSnapshot();
  });
});
