import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@material-ui/core';
import { Field, Formik } from 'formik';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import { DialogFooter } from '../../../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../../../containers/dialogs/DialogTitleWrapper';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { useSnackbar } from '../../../../hooks/useSnackBar';
import { FormikCheckboxField } from '../../../../shared/Formik/FormikCheckboxField';
import {
  GrievanceTicketDocument,
  ProgramNode,
  useAllProgramsQuery,
  useReassignRoleGrievanceMutation,
} from '../../../../__generated__/graphql';
import { LookUpIndividualFilters } from '../LookUpIndividualTable/LookUpIndividualFilters';
import { LookUpIndividualTable } from '../LookUpIndividualTable/LookUpIndividualTable';

export const LookUpReassignRoleModal = ({
  onValueChange,
  initialValues,
  lookUpDialogOpen,
  setLookUpDialogOpen,
  ticket,
  selectedIndividual,
  selectedHousehold,
  setSelectedIndividual,
  setSelectedHousehold,
  individual,
  household,
}: {
  onValueChange;
  initialValues;
  lookUpDialogOpen;
  setLookUpDialogOpen;
  ticket;
  selectedIndividual;
  selectedHousehold;
  setSelectedIndividual;
  setSelectedHousehold;
  individual;
  household?;
}): React.ReactElement => {
  const { t } = useTranslation();
  const { id } = useParams();
  const { showMessage } = useSnackbar();
  const [mutate] = useReassignRoleGrievanceMutation();
  const individualFilterInitial: {
    search;
    programs;
    lastRegistrationDate;
    status;
    admin2;
    sex;
    household?;
  } = {
    search: '',
    programs: '',
    lastRegistrationDate: { min: undefined, max: undefined },
    status: '',
    admin2: null,
    sex: '',
  };
  if (household) {
    individualFilterInitial.household = household?.id;
  }
  const [filterIndividualApplied, setFilterIndividualApplied] = useState(
    individualFilterInitial,
  );
  const [filterIndividual, setFilterIndividual] = useState(
    individualFilterInitial,
  );
  const businessArea = useBusinessArea();
  const { data, loading } = useAllProgramsQuery({
    variables: { businessArea },
    fetchPolicy: 'cache-and-network',
  });

  if (loading) return null;

  const { allPrograms } = data;
  const programs = allPrograms.edges.map((edge) => edge.node);

  const handleCancel = (): void => {
    setLookUpDialogOpen(false);
  };
  return (
    <Formik
      initialValues={initialValues}
      onSubmit={async (values) => {
        onValueChange('selectedHousehold', values.selectedHousehold);
        onValueChange('selectedIndividual', values.selectedIndividual);
        setLookUpDialogOpen(false);

        const multipleRolesVariables = {
          grievanceTicketId: id,
          householdId: household.id,
          newIndividualId: values.selectedIndividual.id,
          individualId: individual.id,
          role: values.role,
        };

        const singleRoleVariables = {
          grievanceTicketId: id,
          householdId: household.id,
          individualId: values.selectedIndividual.id,
          role: values.role,
        };

        const shouldUseMultiple =
          ticket.needsAdjudicationTicketDetails.selectedIndividuals.length;

        try {
          await mutate({
            variables: shouldUseMultiple
              ? multipleRolesVariables
              : singleRoleVariables,
            refetchQueries: () => [
              {
                query: GrievanceTicketDocument,
                variables: { id: ticket.id },
              },
            ],
          });
          showMessage(t('Role Reassigned'));
        } catch (e) {
          e.graphQLErrors.map((x) => showMessage(x.message));
        }
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
              {t('Reassign Role')}
            </DialogTitle>
          </DialogTitleWrapper>
          <DialogContent>
            <LookUpIndividualFilters
              programs={programs as ProgramNode[]}
              filter={filterIndividual}
              onFilterChange={setFilterIndividual}
              setFilterIndividualApplied={setFilterIndividualApplied}
              individualFilterInitial={individualFilterInitial}
              household={household}
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
              ticket={ticket}
              excludedId={individual.id}
              withdrawn={false}
            />
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
                <Button onClick={() => handleCancel()}>{t('CANCEL')}</Button>
                <Button
                  type='submit'
                  color='primary'
                  variant='contained'
                  onClick={submitForm}
                  disabled={values.identityVerified === false}
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
