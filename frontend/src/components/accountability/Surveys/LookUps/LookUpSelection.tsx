import { Box, FormControlLabel, Radio, RadioGroup } from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { SurveyTabsValues } from '../../../../utils/constants';
import {
  ProgramNode,
  useAllProgramsForChoicesQuery,
  useProgrammeChoiceDataQuery,
} from '../../../../__generated__/graphql';
import { LookUpSelectionFilters } from './LookUpSelectionFilters';
import { LookUpSelectionTables } from './LookUpSelectionTables';

const surveysTabs = ['Programme', 'Target Population'];

const BoxWithBorderBottom = styled(Box)`
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
  const filtersProgramInitial = {
    sector: [],
    status: [],
    startDate: undefined,
    endDate: undefined,
    numberOfHouseholds: {
      min: undefined,
      max: undefined,
    },
    budget: {
      min: undefined,
      max: undefined,
    },
  };
  const filtersTargetPopulationInitial = {
    numIndividuals: {
      min: undefined,
      max: undefined,
    },
    createdAtRange: { min: undefined, max: undefined },
    name: '',
    status: '',
  };

  const [filtersProgramApplied, setFiltersProgramApplied] = useState(
    filtersProgramInitial,
  );
  const [
    filtersTargetPopulationApplied,
    setFiltersTargetPopulationApplied,
  ] = useState(filtersTargetPopulationInitial);

  const { t } = useTranslation();

  const {
    data: choicesData,
    loading: choicesLoading,
  } = useProgrammeChoiceDataQuery({
    variables: { businessArea },
  });

  const { data, loading: programsLoading } = useAllProgramsForChoicesQuery({
    variables: { businessArea },
    fetchPolicy: 'cache-and-network',
  });

  const allPrograms = data?.allPrograms?.edges || [];
  const programs = allPrograms.map((edge) => edge.node);

  const handleChange = (type: number, value: string): void => {
    setValues({
      ...values,
      program:
        type === SurveyTabsValues.PROGRAM && typeof value !== 'string'
          ? value
          : '',
      targetPopulation:
        type === SurveyTabsValues.TARGET_POPULATION && typeof value === 'string'
          ? value
          : '',
    });
  };

  if (programsLoading || choicesLoading) return null;

  return (
    <Box>
      <BoxWithBorderBottom
        p={4}
        m={4}
        display='flex'
        alignItems='center'
        bgcolor='#F5F5F5'
      >
        <Box pr={5} fontWeight='500' fontSize='medium'>
          {t('Look up for')}
        </Box>
        <RadioGroup
          aria-labelledby='selection-radio-buttons-group'
          value={selectedTab}
          row
          name='radio-buttons-group'
        >
          {surveysTabs.map((tab, index) => (
            <FormControlLabel
              value={index}
              onChange={() => {
                setSelectedTab(index);
              }}
              control={<Radio color='primary' />}
              label={tab}
              key={tab}
            />
          ))}
        </RadioGroup>
      </BoxWithBorderBottom>
      <Box p={4} mt={4}>
        <LookUpSelectionFilters
          programs={programs as ProgramNode[]}
          choicesData={choicesData}
          setFiltersProgramApplied={setFiltersProgramApplied}
          setFiltersTargetPopulationApplied={setFiltersTargetPopulationApplied}
          selectedTab={selectedTab}
          filtersProgramInitial={filtersProgramInitial}
          filtersTargetPopulationInitial={filtersTargetPopulationInitial}
        />
      </Box>
      <LookUpSelectionTables
        selectedTab={selectedTab}
        choicesData={choicesData}
        filtersProgramApplied={filtersProgramApplied}
        filtersTargetPopulationApplied={filtersTargetPopulationApplied}
        businessArea={businessArea}
        onValueChange={onValueChange}
        values={values}
        handleChange={handleChange}
      />
    </Box>
  );
};
