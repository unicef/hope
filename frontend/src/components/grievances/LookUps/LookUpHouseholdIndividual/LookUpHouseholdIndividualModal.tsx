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
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { DialogFooter } from '../../../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../../../containers/dialogs/DialogTitleWrapper';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { FormikCheckboxField } from '../../../../shared/Formik/FormikCheckboxField';
import { GRIEVANCE_ISSUE_TYPES } from '../../../../utils/constants';
import {
  ProgramNode,
  useAllProgramsForChoicesQuery,
  useHouseholdChoiceDataQuery,
} from '../../../../__generated__/graphql';
import { AutoSubmitFormOnEnter } from '../../../core/AutoSubmitFormOnEnter';
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

export const LookUpHouseholdIndividualModal = ({
  onValueChange,
  initialValues,
  lookUpDialogOpen,
  setLookUpDialogOpen,
  selectedIndividual,
  selectedHousehold,
  setSelectedIndividual,
  setSelectedHousehold,
}: {
  onValueChange;
  initialValues;
  lookUpDialogOpen;
  setLookUpDialogOpen;
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

  const handleCancel = (): void => {
    setLookUpDialogOpen(false);
    setSelectedTab(0);
  };

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

  return (
    <Formik
      initialValues={initialValues}
      enableReinitialize
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
          {lookUpDialogOpen && <AutoSubmitFormOnEnter />}
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
            </DialogTitle>
          </DialogTitleWrapper>
          <DialogContent>
            <TabPanel value={selectedTab} index={0}>
              <LookUpHouseholdFilters
                programs={programs as ProgramNode[]}
                filter={filterHousehold}
                onFilterChange={setFilterHousehold}
                setFilterHouseholdApplied={setFilterHouseholdApplied}
                householdFilterInitial={householdFilterInitial}
                choicesData={choicesData}
              />
              <LookUpHouseholdTable
                filter={filterHouseholdApplied}
                businessArea={businessArea}
                choicesData={choicesData}
                setFieldValue={setFieldValue}
                selectedHousehold={selectedHousehold}
                setSelectedHousehold={setSelectedHousehold}
                setSelectedIndividual={setSelectedIndividual}
              />
            </TabPanel>
            <TabPanel value={selectedTab} index={1}>
              <LookUpIndividualFilters
                programs={programs as ProgramNode[]}
                filter={filterIndividual}
                onFilterChange={setFilterIndividual}
                setFilterIndividualApplied={setFilterIndividualApplied}
                individualFilterInitial={individualFilterInitial}
              />
              <LookUpIndividualTable
                filter={filterIndividualApplied}
                businessArea={businessArea}
                setFieldValue={setFieldValue}
                valuesInner={values}
                selectedHousehold={selectedHousehold}
                setSelectedHousehold={setSelectedHousehold}
                selectedIndividual={selectedIndividual}
                setSelectedIndividual={setSelectedIndividual}
                withdrawn={false}
              />
            </TabPanel>
          </DialogContent>
          <DialogFooter>
            <DialogActions>
              <Box display='flex'>
                <Box mr={1}>
                  <Field
                    name='identityVerified'
                    label={t('Identity Verified*')}
                    component={FormikCheckboxField}
                  />
                </Box>
                <Button onClick={() => handleCancel()}>{t('CANCEL')}</Button>
                <Button
                  color='primary'
                  variant='contained'
                  onClick={async () => {
                    await submitForm();
                  }}
                  disabled={shouldBeDisabled(values)}
                  data-cy='button-submit'
                >
                  {t('SAVE')}
                </Button>
              </Box>
            </DialogActions>
          </DialogFooter>
        </Dialog>
      )}
    </Formik>
  );
};
