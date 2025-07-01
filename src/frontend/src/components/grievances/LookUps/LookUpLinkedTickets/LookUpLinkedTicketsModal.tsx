import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@mui/material';
import { Formik, FormikValues } from 'formik';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { getFilterFromQueryParams } from '@utils/utils';
import { AutoSubmitFormOnEnter } from '@core/AutoSubmitFormOnEnter';
import { LoadingComponent } from '@core/LoadingComponent';
import { LookUpLinkedTicketsFilters } from '../LookUpLinkedTicketsTable/LookUpLinkedTicketsFilters';
import { LookUpLinkedTicketsTable } from '../LookUpLinkedTicketsTable/LookUpLinkedTicketsTable';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';

export const LookUpLinkedTicketsModal = ({
  onValueChange,
  initialValues,
  lookUpDialogOpen,
  setLookUpDialogOpen,
}): ReactElement => {
  const { businessArea } = useBaseUrl();
  const { t } = useTranslation();
  const location = useLocation();
  const { data: choicesData, isLoading: choicesLoading } = useQuery({
    queryKey: ['businessAreasGrievanceTicketsChoices', businessArea],
    queryFn: () =>
      RestService.restBusinessAreasGrievanceTicketsChoicesRetrieve({
        businessAreaSlug: businessArea,
      }),
  });
  const initialFilter = {
    search: '',
    documentType: choicesData?.documentTypeChoices?.[0]?.value,
    documentNumber: '',
    status: '',
    fsp: '',
    createdAtRangeMin: null,
    createdAtRangeMax: null,
    admin2: '',
  };

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );

  if (!choicesData) return null;
  if (choicesLoading) {
    return <LoadingComponent />;
  }
  const handleSubmit = (values: FormikValues): void => {
    onValueChange('selectedLinkedTickets', values.selectedLinkedTickets);
    setLookUpDialogOpen(false);
  };

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={(values) => {
        handleSubmit(values);
      }}
    >
      {({ submitForm, setFieldValue }) => (
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
            <DialogTitle>{t('Look up Linked Tickets')}</DialogTitle>
          </DialogTitleWrapper>
          <DialogContent>
            <LookUpLinkedTicketsFilters
              choicesData={choicesData}
              filter={filter}
              setFilter={setFilter}
              initialFilter={initialFilter}
              appliedFilter={appliedFilter}
              setAppliedFilter={setAppliedFilter}
            />
            <LookUpLinkedTicketsTable
              filter={appliedFilter}
              businessArea={businessArea}
              setFieldValue={setFieldValue}
              initialValues={initialValues}
            />
          </DialogContent>
          <DialogFooter>
            <DialogActions>
              <Button
                data-cy="button-cancel"
                onClick={() => setLookUpDialogOpen(false)}
              >
                {t('CANCEL')}
              </Button>
              <Button
                type="submit"
                color="primary"
                variant="contained"
                onClick={() => {
                  submitForm();
                }}
                data-cy="button-submit"
              >
                {t('SAVE')}
              </Button>
            </DialogActions>
          </DialogFooter>
        </Dialog>
      )}
    </Formik>
  );
};
