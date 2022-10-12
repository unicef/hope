import { Box, Button, Grid } from '@material-ui/core';
import React, { useCallback, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { CommunicationTabsValues } from '../../../../utils/constants';
import {
  HouseholdChoiceDataQuery,
  ProgramNode,
} from '../../../../__generated__/graphql';
import { LookUpHouseholdFilters } from '../../../grievances/LookUps/LookUpHouseholdTable/LookUpHouseholdFilters';
import { RegistrationFilters } from '../../../rdi/RegistrationFilter';
import { TargetPopulationFilters } from '../../../targeting/TargetPopulationFilters';

interface LookUpSelectionFiltersProps {
  selectedTab: number;
  choicesData: HouseholdChoiceDataQuery;
  programs: ProgramNode[];
  setFiltersHouseholdApplied;
  setFiltersTargetPopulationApplied;
  setFiltersRDIApplied;
  filtersInitial;
}
export function LookUpSelectionFilters({
  selectedTab,
  choicesData,
  programs,
  setFiltersHouseholdApplied,
  setFiltersTargetPopulationApplied,
  setFiltersRDIApplied,
  filtersInitial,
}: LookUpSelectionFiltersProps): React.ReactElement {
  const { t } = useTranslation();

  const [filterHousehold, setFilterHousehold] = useState({
    lastRegistrationDate: { min: undefined, max: undefined },
    size: { min: undefined, max: undefined },
  });
  const [filterTargetPopulation, setFilterTargetPopulation] = useState({
    numIndividuals: { min: undefined, max: undefined },
    createdAtRange: { min: undefined, max: undefined },
  });

  const [filterRDI, setFilterRDI] = useState({
    size: { min: undefined, max: undefined },
    importDateRange: { min: undefined, max: undefined },
  });

  const clearFilter = useCallback(() => {
    if (selectedTab === CommunicationTabsValues.HOUSEHOLD) {
      setFiltersHouseholdApplied(filtersInitial);
      setFilterHousehold(filtersInitial);
    } else if (selectedTab === CommunicationTabsValues.TARGET_POPULATION) {
      setFiltersTargetPopulationApplied(filtersInitial);
      setFilterTargetPopulation(filtersInitial);
    } else {
      setFiltersRDIApplied(filtersInitial);
      setFilterRDI(filtersInitial);
    }
  }, [
    filtersInitial,
    selectedTab,
    setFiltersHouseholdApplied,
    setFiltersRDIApplied,
    setFiltersTargetPopulationApplied,
  ]);

  const applyFilter = useCallback(() => {
    if (selectedTab === CommunicationTabsValues.HOUSEHOLD) {
      setFiltersHouseholdApplied(filterHousehold);
    } else if (selectedTab === CommunicationTabsValues.TARGET_POPULATION) {
      setFiltersTargetPopulationApplied(filterTargetPopulation);
    } else {
      setFiltersRDIApplied(filterRDI);
    }
  }, [
    filterHousehold,
    filterRDI,
    filterTargetPopulation,
    selectedTab,
    setFiltersHouseholdApplied,
    setFiltersRDIApplied,
    setFiltersTargetPopulationApplied,
  ]);

  const renderTable = (): React.ReactElement => {
    return (
      <Box>
        {selectedTab === CommunicationTabsValues.HOUSEHOLD && (
          <LookUpHouseholdFilters
            onFilterChange={setFilterHousehold}
            filter={filterHousehold}
            programs={programs}
            choicesData={choicesData}
            addBorder={false}
          />
        )}
        {selectedTab === CommunicationTabsValues.TARGET_POPULATION && (
          <TargetPopulationFilters
            filter={filterTargetPopulation}
            programs={programs}
            onFilterChange={setFilterTargetPopulation}
            addBorder={false}
          />
        )}
        {selectedTab === CommunicationTabsValues.RDI && (
          <RegistrationFilters
            onFilterChange={setFilterRDI}
            filter={filterRDI}
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
}
