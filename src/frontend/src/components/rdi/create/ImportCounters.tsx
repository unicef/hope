import { useTranslation } from 'react-i18next';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useProgramQuery } from '@generated/graphql';
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
  const { programId } = useBaseUrl();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiary_group;

  const { data: programData } = useProgramQuery({
    variables: { id: programId },
  });
  if (!programData) {
    return null;
  }
  if (programData.program.isSocialWorkerProgram) {
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
