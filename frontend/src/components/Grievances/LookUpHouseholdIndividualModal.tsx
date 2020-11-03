import React, { useState } from 'react';
import styled from 'styled-components';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Tab,
  Tabs,
} from '@material-ui/core';
import { TabPanel } from '../TabPanel';
import { useDebounce } from '../../hooks/useDebounce';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import {
  ProgramNode,
  useAllProgramsQuery,
  useHouseholdChoiceDataQuery,
} from '../../__generated__/graphql';
import { LookUpHouseholdFilters } from './LookUpHouseholdTable/LookUpHouseholdFilters';
import { LookUpHouseholdTable } from './LookUpHouseholdTable/LookUpHouseholdTable';
import { LookUpIndividualFilters } from './LookUpIndividualTable/LookUpIndividualFilters';
import { LookUpIndividualTable } from './LookUpIndividualTable/LookUpIndividualTable';
import { Formik } from 'formik';

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;
const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const StyledTabs = styled(Tabs)`
  && {
    max-width: 500px;
  }
`;

export const LookUpHouseholdIndividualModal = ({
  onValueChange,
  initialValues,
  lookUpDialogOpen,
  setLookUpDialogOpen,
}): React.ReactElement => {
  const [selectedTab, setSelectedTab] = useState(0);
  const [filterHousehold, setFilterHousehold] = useState({
    search: '',
    programs: [],
    lastRegistrationDate: { min: undefined, max: undefined },
    residenceStatus: '',
    size: { min: undefined, max: undefined },
    admin2: '',
  });
  const [filterIndividual, setFilterIndividual] = useState({
    search: '',
    program: '',
    lastRegistrationDate: { min: undefined, max: undefined },
    residenceStatus: '',
    admin2: '',
    sex: '',
  });
  const debouncedFilterHousehold = useDebounce(filterHousehold, 500);
  const debouncedFilterIndividual = useDebounce(filterIndividual, 500);
  const businessArea = useBusinessArea();
  const { data, loading } = useAllProgramsQuery({
    variables: { businessArea },
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

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={(values) => {
        console.log('val', values);
        onValueChange('selectedHousehold', values.selectedHousehold);
        onValueChange('selectedIndividual', values.selectedIndividual);
        setLookUpDialogOpen(false);
      }}
      // validationSchema={validationSchema}
    >
      {({ submitForm, values, setValues, setFieldValue }) => (
        <>
          <Dialog
            maxWidth='lg'
            fullWidth
            open={lookUpDialogOpen}
            onClose={() => setLookUpDialogOpen(false)}
            scroll='paper'
            aria-labelledby='form-dialog-title'
          >
            <DialogTitleWrapper>
              <DialogTitle id='scroll-dialog-title'>
                <StyledTabs
                  value={selectedTab}
                  onChange={(
                    event: React.ChangeEvent<{}>,
                    newValue: number,
                  ) => {
                    setSelectedTab(newValue);
                  }}
                  indicatorColor='primary'
                  textColor='primary'
                  variant='fullWidth'
                  aria-label='look up tabs'
                >
                  <Tab label='LOOK UP HOUSEHOLD' />
                  <Tab label='LOOK UP INDIVIDUAL' />
                </StyledTabs>
              </DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              <TabPanel value={selectedTab} index={0}>
                <LookUpHouseholdFilters
                  programs={programs as ProgramNode[]}
                  filter={debouncedFilterHousehold}
                  onFilterChange={setFilterHousehold}
                  choicesData={choicesData}
                />
                <LookUpHouseholdTable
                  filter={debouncedFilterHousehold}
                  businessArea={businessArea}
                  choicesData={choicesData}
                  setFieldValue={setFieldValue}
                  initialValues={initialValues}
                />
              </TabPanel>
              <TabPanel value={selectedTab} index={1}>
                <LookUpIndividualFilters
                  programs={programs as ProgramNode[]}
                  filter={debouncedFilterIndividual}
                  onFilterChange={setFilterIndividual}
                  choicesData={choicesData}
                />
                <LookUpIndividualTable
                  filter={debouncedFilterIndividual}
                  businessArea={businessArea}
                  setFieldValue={setFieldValue}
                  initialValues={initialValues}
                />
              </TabPanel>
            </DialogContent>
            <DialogFooter>
              <DialogActions>
                <Button onClick={() => setLookUpDialogOpen(false)}>
                  CANCEL
                </Button>
                <Button
                  type='submit'
                  color='primary'
                  variant='contained'
                  onClick={submitForm}
                  data-cy='button-submit'
                >
                  SAVE
                </Button>
              </DialogActions>
            </DialogFooter>
          </Dialog>
        </>
      )}
    </Formik>
  );
};
