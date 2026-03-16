import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@mui/material';
import { Formik } from 'formik';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { AutoSubmitFormOnEnter } from '@core/AutoSubmitFormOnEnter';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { IndividualList } from '@restgenerated/models/IndividualList';
import { LookUpIndividualTable } from '../LookUpIndividualTable/LookUpIndividualTable';

const defaultFilter = {
  search: '',
  documentType: '',
  documentNumber: '',
  admin2: '',
  sex: '',
  ageMin: '',
  ageMax: '',
  flags: [],
  orderBy: 'unicef_id',
  status: '',
  programState: 'active',
};

export function LookUpDelegateModal({
  onValueChange,
  initialValues,
  lookUpDialogOpen,
  setLookUpDialogOpen,
}): ReactElement {
  const { t } = useTranslation();
  const { programId } = useBaseUrl();

  const [selectedDelegate, setSelectedDelegate] =
    useState<IndividualList | null>(initialValues.selectedDelegate || null);

  const filter = {
    ...defaultFilter,
    program: programId,
  };

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={(values) => {
        onValueChange('selectedDelegate', values.selectedDelegate);
        setLookUpDialogOpen(false);
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
            <DialogTitle>{t('Update Delegate')}</DialogTitle>
          </DialogTitleWrapper>
          <DialogContent>
            <LookUpIndividualTable
              filter={filter}
              setFieldValue={setFieldValue}
              valuesInner={initialValues}
              selectedHousehold={initialValues.selectedHousehold}
              setSelectedHousehold={() => {}}
              selectedIndividual={selectedDelegate}
              setSelectedIndividual={(individual: IndividualList) => {
                setSelectedDelegate(individual);
                setFieldValue('selectedDelegate', individual);
              }}
              noTableStyling
            />
          </DialogContent>
          <DialogFooter>
            <DialogActions>
              <Button onClick={() => setLookUpDialogOpen(false)}>
                {t('CANCEL')}
              </Button>
              <Button
                type="submit"
                color="primary"
                variant="contained"
                onClick={submitForm}
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
}
