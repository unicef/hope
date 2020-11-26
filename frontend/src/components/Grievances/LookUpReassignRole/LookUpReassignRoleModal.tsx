import React, { useState } from 'react';
import styled from 'styled-components';
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Tab,
  Tabs,
} from '@material-ui/core';
import { Field, Formik } from 'formik';
import { TabPanel } from '../../TabPanel';
import { useDebounce } from '../../../hooks/useDebounce';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import {
  ProgramNode,
  useAllProgramsQuery,
  useHouseholdChoiceDataQuery,
} from '../../../__generated__/graphql';
import { FormikCheckboxField } from '../../../shared/Formik/FormikCheckboxField';
import { LookUpHouseholdFilters } from '../LookUpHouseholdTable/LookUpHouseholdFilters';
import { LookUpHouseholdTable } from '../LookUpHouseholdTable/LookUpHouseholdTable';
import { LookUpIndividualFilters } from '../LookUpIndividualTable/LookUpIndividualFilters';
import { LookUpIndividualTable } from '../LookUpIndividualTable/LookUpIndividualTable';
import { GRIEVANCE_ISSUE_TYPES } from '../../../utils/constants';

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

export const LookUpReassignRoleModal = ({
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

  const handleCancel = (): void => {
    setLookUpDialogOpen(false);
    setSelectedTab(0);
  };
  return (
    <Formik
      initialValues={initialValues}
      onSubmit={(values) => {
        onValueChange('selectedHousehold', values.selectedHousehold);
        onValueChange('selectedIndividual', values.selectedIndividual);
        setLookUpDialogOpen(false);
      }}
    >
      {({ submitForm, setFieldValue, values }) => (
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
                onChange={(event: React.ChangeEvent<{}>, newValue: number) => {
                  setSelectedTab(newValue);
                }}
                indicatorColor='primary'
                textColor='primary'
                variant='fullWidth'
                aria-label='look up tabs'
              >
                <Tab label='LOOK UP HOUSEHOLD' />
                <Tab
                  disabled={
                    initialValues.issueType ===
                    GRIEVANCE_ISSUE_TYPES.ADD_INDIVIDUAL
                  }
                  label='LOOK UP INDIVIDUAL'
                />
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
              />
              <LookUpIndividualTable
                filter={debouncedFilterIndividual}
                businessArea={businessArea}
                setFieldValue={setFieldValue}
                initialValues={initialValues}
                valuesInner={values}
              />
            </TabPanel>
          </DialogContent>
          <DialogFooter>
            <DialogActions>
              <Box display='flex'>
                <Box mr={1}>
                  <Field
                    name='identityVerified'
                    label='Identity Verified*'
                    component={FormikCheckboxField}
                  />
                </Box>
                <Button onClick={() => handleCancel()}>CANCEL</Button>
                <Button
                  type='submit'
                  color='primary'
                  variant='contained'
                  onClick={submitForm}
                  disabled={values.identityVerified === false}
                  data-cy='button-submit'
                >
                  SAVE
                </Button>
              </Box>
            </DialogActions>
          </DialogFooter>
        </Dialog>
      )}
    </Formik>
  );
};
