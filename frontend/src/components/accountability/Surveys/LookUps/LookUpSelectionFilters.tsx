import { Box, Button, Grid } from '@material-ui/core';
import React, { useCallback, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ProgrammesFilters } from '../../../../containers/tables/ProgrammesTable/ProgrammesFilter';
import { SurveyTabsValues } from '../../../../utils/constants';
import {
  ProgrammeChoiceDataQuery,
  ProgramNode,
} from '../../../../__generated__/graphql';
import { TargetPopulationFilters } from '../../../targeting/TargetPopulationFilters';

interface LookUpSelectionFiltersProps {
  selectedTab: number;
  choicesData: ProgrammeChoiceDataQuery;
  programs: ProgramNode[];
  setFiltersProgramApplied;
  setFiltersTargetPopulationApplied;
  filtersProgramInitial;
  filtersTargetPopulationInitial;
}
export const LookUpSelectionFilters = ({
  selectedTab,
  choicesData,
  programs,
  setFiltersProgramApplied,
  setFiltersTargetPopulationApplied,
  filtersProgramInitial,
  filtersTargetPopulationInitial,
}: LookUpSelectionFiltersProps): React.ReactElement => {
  const { t } = useTranslation();

  const [filterProgram, setFilterProgram] = useState(filtersProgramInitial);
  const [filterTargetPopulation, setFilterTargetPopulation] = useState(
    filtersTargetPopulationInitial,
  );

  const clearFilter = useCallback(() => {
    if (selectedTab === SurveyTabsValues.PROGRAM) {
      setFiltersProgramApplied(filtersProgramInitial);
      setFilterProgram(filtersProgramInitial);
    } else if (selectedTab === SurveyTabsValues.TARGET_POPULATION) {
      setFiltersTargetPopulationApplied(filtersTargetPopulationInitial);
      setFilterTargetPopulation(filtersTargetPopulationInitial);
    }
  }, [
    filtersProgramInitial,
    filtersTargetPopulationInitial,
    selectedTab,
    setFiltersProgramApplied,
    setFiltersTargetPopulationApplied,
  ]);

  const applyFilter = useCallback(() => {
    if (selectedTab === SurveyTabsValues.PROGRAM) {
      setFiltersProgramApplied(filterProgram);
    } else if (selectedTab === SurveyTabsValues.TARGET_POPULATION) {
      setFiltersTargetPopulationApplied(filterTargetPopulation);
    }
  }, [
    filterProgram,
    filterTargetPopulation,
    selectedTab,
    setFiltersTargetPopulationApplied,
    setFiltersProgramApplied,
  ]);

  const renderTable = (): React.ReactElement => {
    return (
      <Box>
        {selectedTab === SurveyTabsValues.PROGRAM && (
          <ProgrammesFilters
            onFilterChange={setFilterProgram}
            filter={filterProgram}
            choicesData={choicesData}
          />
        )}
        {selectedTab === SurveyTabsValues.TARGET_POPULATION && (
          <TargetPopulationFilters
            filter={filterTargetPopulation}
            programs={programs}
            onFilterChange={setFilterTargetPopulation}
            addBorder={false}
          />
        )}

        <Grid container justify='flex-end'>
          <Box mt={4}>
            <Button color='primary' onClick={() => clearFilter()}>
              {t('Clear')}
            </Button>
            <Button
              color='primary'
              variant='outlined'
              onClick={() => applyFilter()}
            >
              {t('Apply')}
            </Button>
          </Box>
        </Grid>
      </Box>
    );
  };
  return renderTable();
};
