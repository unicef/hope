import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { AutoSubmitFormOnEnter } from '@core/AutoSubmitFormOnEnter';
import { LoadingComponent } from '@core/LoadingComponent';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@mui/material';
import { IndividualChoices } from '@restgenerated/models/IndividualChoices';
import { GrievanceReassignRole } from '@restgenerated/models/GrievanceReassignRole';
import { RestService } from '@restgenerated/services/RestService';
import { FormikCheckboxField } from '@shared/Formik/FormikCheckboxField';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { getFilterFromQueryParams } from '@utils/utils';
import { Field, Formik } from 'formik';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useParams } from 'react-router-dom';
import { IndividualsFilter } from '../../../population/IndividualsFilter';
import { LookUpIndividualTable } from '../LookUpIndividualTable/LookUpIndividualTable';
import { HouseholdDetail } from '@restgenerated/models/HouseholdDetail';

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
  selectedHousehold: HouseholdDetail;
  setSelectedIndividual;
  setSelectedHousehold;
  shouldUseMultiple;
  individual;
  household?;
}): ReactElement {
  const { t } = useTranslation();
  const location = useLocation();
  const { businessArea } = useBaseUrl();

  const { id } = useParams();
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();

  const { mutateAsync: reassignRole } = useMutation({
    mutationFn: (formData: GrievanceReassignRole) => {
      return RestService.restBusinessAreasGrievanceTicketsReassignRoleCreate({
        businessAreaSlug: businessArea,
        id: id,
        formData,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['businessAreasGrievanceTicketsRetrieve', businessArea, id],
      });
      showMessage(t('Role Reassigned'));
    },
    onError: (error: any) => {
      const errorMessage =
        error?.body?.errors || error?.message || 'An error occurred';
      showMessage(errorMessage);
    },
  });

  const { data: individualChoicesData, isLoading: individualChoicesLoading } =
    useQuery<IndividualChoices>({
      queryKey: ['individualChoices', businessArea],
      queryFn: () =>
        RestService.restBusinessAreasIndividualsChoicesRetrieve({
          businessAreaSlug: businessArea,
        }),
    });

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

        const requestBody: GrievanceReassignRole = {
          householdId: household.id,
          individualId: shouldUseMultiple
            ? individual.id
            : values.selectedIndividual?.id,
          newIndividualId: shouldUseMultiple
            ? values.selectedIndividual?.id
            : undefined,
          role: values.role,
        };

        try {
          await reassignRole(requestBody);
        } catch (e) {
          // Error handled in onError callback
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
