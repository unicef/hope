import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { AutoSubmitFormOnEnter } from '@core/AutoSubmitFormOnEnter';
import { LoadingComponent } from '@core/LoadingComponent';
import { useBaseUrl } from '@hooks/useBaseUrl';
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@mui/material';
import { IndividualChoices } from '@restgenerated/models/IndividualChoices';
import { RestService } from '@restgenerated/services/RestService';
import { FormikCheckboxField } from '@shared/Formik/FormikCheckboxField';
import { useQuery } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import { getFilterFromQueryParams } from '@utils/utils';
import { Field, Formik } from 'formik';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { IndividualsFilter } from '../../population/IndividualsFilter';
import { LookUpIndividualTable } from '../LookUps/LookUpIndividualTable/LookUpIndividualTable';
import { NaIndividual, roleLabel } from './naRoleUtils';
import { NaRequiredRole } from './naTypes';

interface NaReassignRoleModalProps {
  open: boolean;
  onClose: () => void;
  role: NaRequiredRole;
  household: { id: string; unicefId: string };
  individualToReassign: NaIndividual;
  // everyone this ticket withdraws; a replacement cannot be one of them
  duplicateIndividualIds: string[];
  onSelect: (individual: { id: string; fullName?: string }) => void;
}

/**
 * Deferred variant of LookUpReassignRoleModal: it hands the picked individual
 * back to the caller instead of POSTing to /reassign-role/. The NA management
 * screen has no per-ticket approval step, so the choice has to stay in session
 * state until the bulk execute.
 */
export const NaReassignRoleModal = ({
  open,
  onClose,
  role,
  household,
  individualToReassign,
  duplicateIndividualIds,
  onSelect,
}: NaReassignRoleModalProps): ReactElement => {
  const { t } = useTranslation();
  const location = useLocation();
  const { businessArea } = useBaseUrl();

  const { data: individualChoicesData, isLoading: individualChoicesLoading } =
    useQuery<IndividualChoices>({
      queryKey: restQueryKey(
        RestService.restBusinessAreasIndividualsChoicesRetrieve,
        { businessAreaSlug: businessArea },
      ),
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
    // The head of household must be a member of that household; a primary
    // collector may be someone outside it.
    household: role === 'HEAD' ? household.id : '',
  };

  const [filterIND, setFilterIND] = useState(
    getFilterFromQueryParams(location, initialFilterIND),
  );
  const [appliedFilterIND, setAppliedFilterIND] = useState(
    getFilterFromQueryParams(location, initialFilterIND),
  );
  const [selectedIndividual, setSelectedIndividual] = useState(null);
  const [selectedHousehold, setSelectedHousehold] = useState(null);

  // under `programs/all` nothing else scopes the lookup, and a cross-programme pick is rejected
  const programScopedFilter = {
    ...appliedFilterIND,
    program: individualToReassign.program ?? '',
  };

  const excludedIds = Array.from(
    new Set([individualToReassign.id, ...duplicateIndividualIds]),
  ).join(',');

  if (individualChoicesLoading) return <LoadingComponent />;
  if (!individualChoicesData) return null;

  return (
    <Formik
      initialValues={{
        selectedIndividual: null,
        selectedHousehold: null,
        identityVerified: false,
      }}
      onSubmit={(values) => {
        if (values.selectedIndividual) {
          onSelect(values.selectedIndividual);
        }
        onClose();
      }}
    >
      {({ submitForm, setFieldValue, values }) => (
        <Dialog
          maxWidth="lg"
          fullWidth
          open={open}
          onClose={onClose}
          scroll="paper"
          aria-labelledby="form-dialog-title"
        >
          {open && <AutoSubmitFormOnEnter />}
          <DialogTitleWrapper>
            <DialogTitle>
              {t('Reassign Role')}: {t(roleLabel(role))} —{' '}
              {household.unicefId}
            </DialogTitle>
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
              filter={programScopedFilter}
              setFieldValue={setFieldValue}
              valuesInner={values}
              selectedHousehold={selectedHousehold}
              setSelectedHousehold={setSelectedHousehold}
              selectedIndividual={selectedIndividual}
              setSelectedIndividual={setSelectedIndividual}
              excludedId={excludedIds}
              noTableStyling
            />
          </DialogContent>
          <DialogFooter>
            <DialogActions>
              <Box sx={{ display: 'flex' }}>
                <Box sx={{ mr: 1 }}>
                  <Field
                    name="identityVerified"
                    label="Identity Verified*"
                    component={FormikCheckboxField}
                  />
                </Box>
                <Button onClick={onClose} data-cy="button-na-reassign-cancel">
                  {t('CANCEL')}
                </Button>
                <Button
                  type="submit"
                  color="primary"
                  variant="contained"
                  disabled={!values.identityVerified || !values.selectedIndividual}
                  onClick={submitForm}
                  data-cy="button-na-reassign-save"
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
