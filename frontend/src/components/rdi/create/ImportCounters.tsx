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
      <div>
        {numberOfHouseholds}{' '}
        {t(
          'Household'
            .concat(numberOfHouseholds > 1 ? 's' : '')
            .concat(' available to import'),
        )}
      </div>
      <div>
        {numberOfIndividuals}{' '}
        {t(
          'Individual'
            .concat(numberOfIndividuals > 1 ? 's' : '')
            .concat(' available to import'),
        )}
      </div>
    </>
  );
}
