import { HouseholdDetail } from '@restgenerated/models/HouseholdDetail';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useProgramContext } from 'src/programContext';
import { CompositionTable } from './CompositionTable';

export interface HouseholdCompositionTableProps {
  household: HouseholdDetail;
}

export function HouseholdCompositionTable({
  household,
}: HouseholdCompositionTableProps): ReactElement {
  const { t } = useTranslation();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  return (
    <CompositionTable
      title={`${beneficiaryGroup?.groupLabel} Composition`}
      rows={[
        {
          ageGroup: '0 - 5',
          dataCy: 'row05',
          female: household?.femaleAgeGroup05Count,
          femaleDisabled: household?.femaleAgeGroup05DisabledCount,
          male: household?.maleAgeGroup05Count,
          maleDisabled: household?.maleAgeGroup05DisabledCount,
        },
        {
          ageGroup: '6 - 11',
          female: household?.femaleAgeGroup611Count,
          femaleDisabled: household?.femaleAgeGroup611DisabledCount,
          male: household?.maleAgeGroup611Count,
          maleDisabled: household?.maleAgeGroup611DisabledCount,
        },
        {
          ageGroup: '12 - 17',
          female: household?.femaleAgeGroup1217Count,
          femaleDisabled: household?.femaleAgeGroup1217DisabledCount,
          male: household?.maleAgeGroup1217Count,
          maleDisabled: household?.maleAgeGroup1217DisabledCount,
        },
        {
          ageGroup: '18 - 59',
          female: household?.femaleAgeGroup1859Count,
          femaleDisabled: household?.femaleAgeGroup1859DisabledCount,
          pregnant: household?.pregnantCount,
          male: household?.maleAgeGroup1859Count,
          maleDisabled: household?.maleAgeGroup1859DisabledCount,
        },
        {
          ageGroup: '60 +',
          female: household?.femaleAgeGroup60Count,
          femaleDisabled: household?.femaleAgeGroup60DisabledCount,
          male: household?.maleAgeGroup60Count,
          maleDisabled: household?.maleAgeGroup60DisabledCount,
        },
      ]}
      footer={[
        { label: t('Other'), value: household?.otherSexGroupCount },
      ]}
    />
  );
}
