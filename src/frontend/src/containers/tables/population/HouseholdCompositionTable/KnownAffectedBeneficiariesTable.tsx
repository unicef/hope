import { HouseholdDetail } from '@restgenerated/models/HouseholdDetail';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { CompositionTable } from './CompositionTable';

export interface KnownAffectedBeneficiariesTableProps {
  household: HouseholdDetail;
}

export function KnownAffectedBeneficiariesTable({
  household,
}: KnownAffectedBeneficiariesTableProps): ReactElement {
  const { t } = useTranslation();
  return (
    <CompositionTable
      dataCy="known-affected-beneficiaries"
      title={t('Known Affected Beneficiaries')}
      rows={[
        {
          ageGroup: '0 - 5',
          dataCy: 'kab-row05',
          female: household?.kabFemaleAgeGroup05Count,
          femaleDisabled: household?.kabFemaleAgeGroup05DisabledCount,
          male: household?.kabMaleAgeGroup05Count,
          maleDisabled: household?.kabMaleAgeGroup05DisabledCount,
        },
        {
          ageGroup: '6 - 11',
          female: household?.kabFemaleAgeGroup611Count,
          femaleDisabled: household?.kabFemaleAgeGroup611DisabledCount,
          male: household?.kabMaleAgeGroup611Count,
          maleDisabled: household?.kabMaleAgeGroup611DisabledCount,
        },
        {
          ageGroup: '12 - 17',
          female: household?.kabFemaleAgeGroup1217Count,
          femaleDisabled: household?.kabFemaleAgeGroup1217DisabledCount,
          male: household?.kabMaleAgeGroup1217Count,
          maleDisabled: household?.kabMaleAgeGroup1217DisabledCount,
        },
        {
          ageGroup: '18 - 59',
          female: household?.kabFemaleAgeGroup1859Count,
          femaleDisabled: household?.kabFemaleAgeGroup1859DisabledCount,
          pregnant: household?.kabPregnantCount,
          male: household?.kabMaleAgeGroup1859Count,
          maleDisabled: household?.kabMaleAgeGroup1859DisabledCount,
        },
        {
          ageGroup: '60 +',
          female: household?.kabFemaleAgeGroup60Count,
          femaleDisabled: household?.kabFemaleAgeGroup60DisabledCount,
          male: household?.kabMaleAgeGroup60Count,
          maleDisabled: household?.kabMaleAgeGroup60DisabledCount,
        },
      ]}
      footer={[
        {
          label: t('Other'),
          value: household?.kabOtherSexGroupCount,
          dataCy: 'kab-other',
        },
        {
          label: t('Unknown'),
          value: household?.kabUnknownSexGroupCount,
          dataCy: 'kab-unknown',
        },
        { label: t('Size'), value: household?.kabSize, dataCy: 'kab-size' },
      ]}
    />
  );
}
