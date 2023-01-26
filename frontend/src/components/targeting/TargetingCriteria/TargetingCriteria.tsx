import React, { useEffect, useState } from 'react';
import { TargetPopulationQuery } from '../../../__generated__/graphql';
import { UniversalCriteriaPaperComponent } from '../../core/UniversalCriteriaComponent/UniversalCriteriaPaperComponent';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useCachedImportedIndividualFieldsQuery } from '../../../hooks/useCachedImportedIndividualFields';
import { VulnerabilityScoreComponent } from './VulnerabilityScoreComponent';

interface TargetingCriteriaProps {
  rules?;
  helpers?;
  targetPopulation?: TargetPopulationQuery['targetPopulation'];
  selectedProgram?;
  isEdit?: boolean;
  disabled?: boolean;
}
const associatedWith = (type) => (item) => item.associatedWith === type;
const isNot = (type) => (item) => item.type !== type;
export function TargetingCriteria({
  rules,
  helpers,
  targetPopulation,
  selectedProgram,
  isEdit,
  disabled,
}: TargetingCriteriaProps): React.ReactElement {
  const [individualData, setIndividualData] = useState(null);
  const [householdData, setHouseholdData] = useState(null);
  const businessArea = useBusinessArea();
  const { data, loading } = useCachedImportedIndividualFieldsQuery(
    businessArea,
  );
  useEffect(() => {
    if (loading) return;
    const filteredIndividualData = {
      allFieldsAttributes: data?.allFieldsAttributes
        ?.filter(associatedWith('Individual'))
        .filter(isNot('IMAGE')),
    };
    setIndividualData(filteredIndividualData);

    const filteredHouseholdData = {
      allFieldsAttributes: data?.allFieldsAttributes?.filter(
        associatedWith('Household'),
      ),
    };
    setHouseholdData(filteredHouseholdData);
  }, [data, loading]);
  return (
    <div>
      <UniversalCriteriaPaperComponent
        title='Example Paper Criteria'
        isEdit={isEdit}
        arrayHelpers={helpers}
        rules={rules}
        disabled={disabled}
        individualDataNeeded={selectedProgram?.individualDataNeeded}
        householdFieldsChoices={householdData?.allFieldsAttributes || []}
        individualFieldsChoices={individualData?.allFieldsAttributes || []}
      />

      {targetPopulation && (
        <VulnerabilityScoreComponent targetPopulation={targetPopulation} />
      )}
    </div>
  );
}
