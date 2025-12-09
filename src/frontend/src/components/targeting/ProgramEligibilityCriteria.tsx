import React from 'react';
import { Example } from '../core/UniversalCriteriaComponent/example';
import withErrorBoundary from '@components/core/withErrorBoundary';

export const ProgramEligibilityCriteria: React.FC = () => {
  return (
    <div>
      <Example />
    </div>
  );
};

export default withErrorBoundary(
  ProgramEligibilityCriteria,
  'ProgramEligibilityCriteria',
);
