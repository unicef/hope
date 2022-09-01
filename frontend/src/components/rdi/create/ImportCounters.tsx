import React from 'react';
import { useTranslation } from 'react-i18next';

export interface ImportCountersPropTypes {
  numberOfHouseholds: number;
  numberOfIndividuals: number;
}

export function ImportCounters({
  numberOfHouseholds,
  numberOfIndividuals,
}: ImportCountersPropTypes): React.ReactElement {
  const { t } = useTranslation();
  return (
    <>
      <div data-cy='number-of-households'>
        {numberOfHouseholds}{' '}
        {t(
          numberOfHouseholds === 1
            ? 'Household available to Import'
            : 'Households available to Import',
        )}
      </div>
      <div data-cy='number-of-individuals'>
        {numberOfIndividuals}{' '}
        {t(
          numberOfIndividuals === 1
            ? 'Individual available to Import'
            : 'Individuals available to Import',
        )}
      </div>
    </>
  );
}
