import React, {Fragment, useEffect, useState} from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { Button, Paper, Typography } from '@material-ui/core';
import { AddCircleOutline } from '@material-ui/icons';
import { TargetCriteriaForm } from '../../../containers/forms/TargetCriteriaForm';
import { TargetPopulationQuery } from '../../../__generated__/graphql';
import { Criteria } from './Criteria';
import {
  ContentWrapper,
  VulnerabilityScoreComponent,
} from './VulnerabilityScoreComponent';
import {UniversalCriteriaPaperComponent} from "../../core/UniversalCriteriaComponent/UniversalCriteriaPaperComponent";
import {useBusinessArea} from "../../../hooks/useBusinessArea";
import {useCachedImportedIndividualFieldsQuery} from "../../../hooks/useCachedImportedIndividualFields";

interface TargetingCriteriaProps {
  rules?;
  helpers?;
  targetPopulation?: TargetPopulationQuery['targetPopulation'];
  selectedProgram?;
  isEdit?: boolean;
}
const associatedWith = (type) => (item) => item.associatedWith === type;
const isNot = (type) => (item) => item.type !== type;
export function TargetingCriteria({
                                    rules,
                                    helpers,
                                    targetPopulation,
                                    selectedProgram,
                                    isEdit,
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
            individualDataNeeded={selectedProgram?.individualDataNeeded}
            householdFieldsChoices={householdData?.allFieldsAttributes||[]}
            individualFieldsChoices={individualData?.allFieldsAttributes||[]}

        />

        {targetPopulation && (
            <VulnerabilityScoreComponent targetPopulation={targetPopulation} />
        )}
      </div>
  );
}
