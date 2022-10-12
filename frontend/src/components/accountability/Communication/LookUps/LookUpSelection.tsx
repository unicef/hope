import { Box, FormControlLabel, Radio, RadioGroup } from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { CommunicationTabsValues } from '../../../../utils/constants';
import {
  ProgramNode,
  useAllProgramsForChoicesQuery,
  useHouseholdChoiceDataQuery,
} from '../../../../__generated__/graphql';
import { LookUpSelectionFilters } from './LookUpSelectionFilters';
import { LookUpSelectionTables } from './LookUpSelectionTables';

const communicationTabs = ['Household', 'Target Population', 'RDI'];

const BoxWithBorderBottom = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  padding: 15px 0;
`;

export const LookUpSelection = ({
  businessArea,
  onValueChange,
  setValues,
  values,
  selectedTab,
  setSelectedTab,
}: {
  businessArea: string;
  onValueChange;
  setValues;
  values;
  selectedTab;
  setSelectedTab;
}): React.ReactElement => {
  const filtersInitial = {
    lastRegistrationDate: { min: undefined, max: undefined },
    size: { min: undefined, max: undefined },
    numIndividuals: { min: undefined, max: undefined },
  };
  const [filtersHouseholdApplied, setFiltersHouseholdApplied] = useState(
    filtersInitial,
  );
  const [
    filtersTargetPopulationApplied,
    setFiltersTargetPopulationApplied,
  ] = useState(filtersInitial);
  const [filtersRDIApplied, setFiltersRDIApplied] = useState(filtersInitial);

  const { t } = useTranslation();

  const {
    data: choicesData,
    loading: choicesLoading,
  } = useHouseholdChoiceDataQuery({
    variables: { businessArea },
  });

  const { data, loading: programsLoading } = useAllProgramsForChoicesQuery({
    variables: { businessArea },
    fetchPolicy: 'cache-and-network',
  });

  const allPrograms = data?.allPrograms?.edges || [];
  const programs = allPrograms.map((edge) => edge.node);

  const handleChange = (type: number, value: string[] | string): void => {
    setValues({
      ...values,
      households:
        type === CommunicationTabsValues.HOUSEHOLD && typeof value !== 'string'
          ? value
          : [],
      targetPopulation:
        type === CommunicationTabsValues.TARGET_POPULATION &&
        typeof value === 'string'
          ? value
          : '',
      registrationDataImport:
        type === CommunicationTabsValues.RDI && typeof value === 'string'
          ? value
          : '',
    });
  };

  if (programsLoading || choicesLoading) return null;

  return (
    <Box>
      <BoxWithBorderBottom>
        <Box p={4} m={4} display='flex' alignItems='center' bgcolor='#F5F5F5'>
          <Box pr={5} fontWeight='500' fontSize='medium'>
            {t('Look up for')}
          </Box>
          <RadioGroup
            aria-labelledby='selection-radio-buttons-group'
            value={selectedTab}
            row
            name='radio-buttons-group'
          >
            {communicationTabs.map((tab, index) => (
              <FormControlLabel
                value={index}
                onChange={() => {
                  setSelectedTab(index);
                }}
                control={<Radio />}
                label={tab}
                key={tab}
              />
            ))}
          </RadioGroup>
        </Box>
      </BoxWithBorderBottom>
      <Box p={4} mt={4}>
        <LookUpSelectionFilters
          programs={programs as ProgramNode[]}
          choicesData={choicesData}
          setFiltersHouseholdApplied={setFiltersHouseholdApplied}
          setFiltersTargetPopulationApplied={setFiltersTargetPopulationApplied}
          setFiltersRDIApplied={setFiltersRDIApplied}
          selectedTab={selectedTab}
          filtersInitial={filtersInitial}
        />
      </Box>
      <LookUpSelectionTables
        selectedTab={selectedTab}
        choicesData={choicesData}
        filtersHouseholdApplied={filtersHouseholdApplied}
        filtersTargetPopulationApplied={filtersTargetPopulationApplied}
        filtersRDIApplied={filtersRDIApplied}
        businessArea={businessArea}
        onValueChange={onValueChange}
        values={values}
        handleChange={handleChange}
      />
    </Box>
  );
};
