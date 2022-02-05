import React, { useEffect } from 'react';
import {useTranslation} from "react-i18next";

export interface ImportCountersPropTypes {
  numberOfHouseholds: number;
  numberOfIndividuals: number;
}

export function ImportCounters({ numberOfHouseholds, numberOfIndividuals}:ImportCountersPropTypes): React.ReactElement {
  const { t } = useTranslation();
  return (
    <>
      <div>
        {numberOfHouseholds}{' '}
        {t('Households available to Import')}
      </div>
      <div>
        {numberOfIndividuals}{' '}
        {t('Individuals available to Import')}
      </div>
    </>
  );
}
