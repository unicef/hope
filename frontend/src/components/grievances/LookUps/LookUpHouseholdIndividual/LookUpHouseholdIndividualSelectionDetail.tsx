import { Box, Tab, Tabs } from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { GRIEVANCE_ISSUE_TYPES } from '../../../../utils/constants';
import {
  ProgramNode,
  useAllProgramsForChoicesQuery,
  useHouseholdChoiceDataQuery,
} from '../../../../__generated__/graphql';
import { TabPanel } from '../../../core/TabPanel';
import { LookUpHouseholdFilters } from '../LookUpHouseholdTable/LookUpHouseholdFilters';
import { LookUpHouseholdTable } from '../LookUpHouseholdTable/LookUpHouseholdTable';
import { LookUpIndividualFilters } from '../LookUpIndividualTable/LookUpIndividualFilters';
import { LookUpIndividualTable } from '../LookUpIndividualTable/LookUpIndividualTable';

const StyledTabs = styled(Tabs)`
  && {
    max-width: 500px;
  }
`;

export const LookUpHouseholdIndividualSelectionDetail = ({
  onValueChange,
  initialValues,
  selectedIndividual,
  selectedHousehold,
  setSelectedIndividual,
  setSelectedHousehold,
}: {
  onValueChange;
  initialValues;
  selectedIndividual;
  selectedHousehold;
  setSelectedIndividual;
  setSelectedHousehold;
}): React.ReactElement => {
  const { t } = useTranslation();
  const [selectedTab, setSelectedTab] = useState(0);
  const householdFilterInitial = {
    search: '',
    programs: [],
    lastRegistrationDate: { min: undefined, max: undefined },
    residenceStatus: '',
    size: { min: undefined, max: undefined },
    admin2: null,
  };
  const [filterHouseholdApplied, setFilterHouseholdApplied] = useState(
    householdFilterInitial,
  );
  const [filterHousehold, setFilterHousehold] = useState(
    householdFilterInitial,
  );

  const individualFilterInitial = {
    search: '',
    programs: '',
    lastRegistrationDate: { min: undefined, max: undefined },
    status: '',
    admin2: null,
    sex: '',
  };
  const [filterIndividualApplied, setFilterIndividualApplied] = useState(
    individualFilterInitial,
  );
  const [filterIndividual, setFilterIndividual] = useState(
    individualFilterInitial,
  );

  const businessArea = useBusinessArea();
  const { data, loading } = useAllProgramsForChoicesQuery({
    variables: { businessArea },
    fetchPolicy: 'cache-and-network',
  });
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useHouseholdChoiceDataQuery({
    variables: { businessArea },
  });
  if (loading || choicesLoading) return null;

  const { allPrograms } = data;
  const programs = allPrograms.edges.map((edge) => edge.node);

  const shouldBeDisabled = (values): boolean => {
    const individualRequiredIssueTypes = [
      GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL,
      GRIEVANCE_ISSUE_TYPES.DELETE_INDIVIDUAL,
    ];
    const householdRequiredIssueTypes = [
      GRIEVANCE_ISSUE_TYPES.EDIT_HOUSEHOLD,
      GRIEVANCE_ISSUE_TYPES.DELETE_HOUSEHOLD,
    ];
    const isHouseholdRequired = householdRequiredIssueTypes.includes(
      values.issueType,
    );
    const isIndividualRequired = individualRequiredIssueTypes.includes(
      values.issueType,
    );
    let result = false;
    if (isIndividualRequired) {
      result = !selectedIndividual || !values.identityVerified;
    } else if (isHouseholdRequired) {
      result = !selectedHousehold || !values.identityVerified;
    } else {
      result = !values.identityVerified;
    }
    return result;
  };

  const onSelect = (key, value): void => {
    onValueChange(key, value);
  };

  return (
    <>
      <Box>
        <Box id='scroll-dialog-title'>
          <StyledTabs
            value={selectedTab}
            onChange={(event: React.ChangeEvent<{}>, newValue: number) => {
              setSelectedTab(newValue);
            }}
            indicatorColor='primary'
            textColor='primary'
            variant='fullWidth'
            aria-label='look up tabs'
          >
            <Tab label={t('LOOK UP HOUSEHOLD')} />
            <Tab
              disabled={
                initialValues.issueType ===
                  GRIEVANCE_ISSUE_TYPES.ADD_INDIVIDUAL ||
                initialValues.issueType ===
                  GRIEVANCE_ISSUE_TYPES.DELETE_HOUSEHOLD
              }
              label={t('LOOK UP INDIVIDUAL')}
            />
          </StyledTabs>
        </Box>
      </Box>
      <Box>
        <TabPanel value={selectedTab} index={0}>
          <LookUpHouseholdFilters
            programs={programs as ProgramNode[]}
            filter={filterHousehold}
            onFilterChange={setFilterHousehold}
            setFilterHouseholdApplied={setFilterHouseholdApplied}
            householdFilterInitial={householdFilterInitial}
            choicesData={choicesData}
            addBorder={false}
          />
          <LookUpHouseholdTable
            filter={filterHouseholdApplied}
            businessArea={businessArea}
            choicesData={choicesData}
            setFieldValue={(key, value) => onSelect(key, value)}
            selectedHousehold={selectedHousehold}
            setSelectedHousehold={setSelectedHousehold}
            setSelectedIndividual={setSelectedIndividual}
            noTableStyling
          />
        </TabPanel>
        <TabPanel value={selectedTab} index={1}>
          <LookUpIndividualFilters
            programs={programs as ProgramNode[]}
            filter={filterIndividual}
            onFilterChange={setFilterIndividual}
            setFilterIndividualApplied={setFilterIndividualApplied}
            individualFilterInitial={individualFilterInitial}
            addBorder={false}
          />
          <LookUpIndividualTable
            filter={filterIndividualApplied}
            businessArea={businessArea}
            setFieldValue={(key, value) => onSelect(key, value)}
            valuesInner={initialValues}
            selectedHousehold={selectedHousehold}
            setSelectedHousehold={setSelectedHousehold}
            selectedIndividual={selectedIndividual}
            setSelectedIndividual={setSelectedIndividual}
            withdrawn={false}
            noTableStyling
          />
        </TabPanel>
      </Box>
    </>
  );
};
