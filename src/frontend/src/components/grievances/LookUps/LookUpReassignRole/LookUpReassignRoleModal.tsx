import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@mui/material';
import { Field, Formik } from 'formik';
import * as React from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useParams } from 'react-router-dom';
import {
  GrievanceTicketDocument,
  useIndividualChoiceDataQuery,
  useReassignRoleGrievanceMutation,
} from '@generated/graphql';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { useSnackbar } from '@hooks/useSnackBar';
import { FormikCheckboxField } from '@shared/Formik/FormikCheckboxField';
import { getFilterFromQueryParams } from '@utils/utils';
import { AutoSubmitFormOnEnter } from '@core/AutoSubmitFormOnEnter';
import { LoadingComponent } from '@core/LoadingComponent';
import { IndividualsFilter } from '../../../population/IndividualsFilter';
import { LookUpIndividualTable } from '../LookUpIndividualTable/LookUpIndividualTable';
import { useBaseUrl } from '@hooks/useBaseUrl';

export function LookUpReassignRoleModal({
  onValueChange,
  initialValues,
  lookUpDialogOpen,
  setLookUpDialogOpen,
  ticket,
  selectedIndividual,
  selectedHousehold,
  setSelectedIndividual,
  setSelectedHousehold,
  shouldUseMultiple,
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
  shouldUseMultiple;
  individual;
  household?;
}): React.ReactElement {
  const { t } = useTranslation();
  const location = useLocation();
  const { id } = useParams();
  const { showMessage } = useSnackbar();
  const [mutate] = useReassignRoleGrievanceMutation();
  const { data: individualChoicesData, loading: individualChoicesLoading } =
    useIndividualChoiceDataQuery();

  const initialFilterIND = {
    search: '',
    documentType: individualChoicesData?.documentTypeChoices?.[0]?.value,
    documentNumber: '',
    admin2: '',
    sex: '',
    ageMin: '',
    ageMax: '',
    flags: [],
    orderBy: 'unicef_id',
    status: '',
    household: '',
  };

  if (household) {
    initialFilterIND.household = household?.id;
  }

  const [filterIND, setFilterIND] = useState(
    getFilterFromQueryParams(location, initialFilterIND),
  );
  const [appliedFilterIND, setAppliedFilterIND] = useState(
    getFilterFromQueryParams(location, initialFilterIND),
  );

  const { businessArea } = useBaseUrl();

  if (individualChoicesLoading) return <LoadingComponent />;

  if (!individualChoicesData) {
    return null;
  }

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
          newIndividualId: values.selectedIndividual?.id,
          individualId: individual.id,
          role: values.role,
        };

        const singleRoleVariables = {
          grievanceTicketId: id,
          householdId: household.id,
          individualId: values.selectedIndividual?.id,
          role: values.role,
        };

        const variables = shouldUseMultiple
          ? multipleRolesVariables
          : singleRoleVariables;

        try {
          await mutate({
            variables,
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
          maxWidth="lg"
          fullWidth
          open={lookUpDialogOpen}
          onClose={() => setLookUpDialogOpen(false)}
          scroll="paper"
          aria-labelledby="form-dialog-title"
        >
          {lookUpDialogOpen && <AutoSubmitFormOnEnter />}
          <DialogTitleWrapper>
            <DialogTitle>{t('Reassign Role')}</DialogTitle>
          </DialogTitleWrapper>
          <DialogContent>
            <IndividualsFilter
              filter={filterIND}
              choicesData={individualChoicesData}
              setFilter={setFilterIND}
              initialFilter={initialFilterIND}
              appliedFilter={appliedFilterIND}
              setAppliedFilter={setAppliedFilterIND}
              isOnPaper={false}
            />
            <LookUpIndividualTable
              filter={appliedFilterIND}
              businessArea={businessArea}
              setFieldValue={setFieldValue}
              valuesInner={values}
              selectedHousehold={selectedHousehold}
              setSelectedHousehold={setSelectedHousehold}
              selectedIndividual={selectedIndividual}
              setSelectedIndividual={setSelectedIndividual}
              ticket={ticket}
              excludedId={individual.id}
              noTableStyling
            />
          </DialogContent>
          <DialogFooter>
            <DialogActions>
              <Box display="flex">
                <Box mr={1}>
                  <Field
                    name="identityVerified"
                    label="Identity Verified*"
                    component={FormikCheckboxField}
                  />
                </Box>
                <Button onClick={() => handleCancel()}>{t('CANCEL')}</Button>
                <Button
                  type="submit"
                  color="primary"
                  variant="contained"
                  onClick={submitForm}
                  disabled={values.identityVerified === false}
                  data-cy="button-submit"
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
}
