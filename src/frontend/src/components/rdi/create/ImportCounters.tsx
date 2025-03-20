import { useTranslation } from 'react-i18next';
import { useProgramContext } from 'src/programContext';
import { ReactElement } from 'react';

export interface ImportCountersPropTypes {
  numberOfHouseholds: number;
  numberOfIndividuals: number;
}

export function ImportCounters({
  numberOfHouseholds,
  numberOfIndividuals,
}: ImportCountersPropTypes): ReactElement {
  const { t } = useTranslation();
  const { selectedProgram, isSocialDctType } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiary_group;

  if (isSocialDctType) {
    return (
      <>
        <div data-cy="number-of-households">
          {numberOfIndividuals} {t(' people available to import')}
        </div>
      </>
    );
  }
  return (
    <>
      <div data-cy="number-of-households">
        {numberOfHouseholds}{' '}
        {t(
          `${beneficiaryGroup?.group_label}`
            .concat(numberOfHouseholds > 1 ? 's' : '')
            .concat(' available to import'),
        )}
      </div>
      <div data-cy="number-of-individuals">
        {numberOfIndividuals}{' '}
        {t(
          `${beneficiaryGroup?.member_label}`
            .concat(numberOfIndividuals > 1 ? 's' : '')
            .concat(' available to import'),
        )}
      </div>
    </>
  );
}
