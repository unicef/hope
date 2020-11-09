import React, { useState } from 'react';
import styled from 'styled-components';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@material-ui/core';
import { Formik } from 'formik';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useDebounce } from '../../../hooks/useDebounce';
import { useGrievancesChoiceDataQuery } from '../../../__generated__/graphql';
import { LookUpRelatedTicketsFilters } from '../LookUpRelatedTicketsTable/LookUpRelatedTicketsFilters';
import { LookUpRelatedTicketsTable } from '../LookUpRelatedTicketsTable/LookUpRelatedTicketsTable';
import { LoadingComponent } from '../../LoadingComponent';

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;
const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

export const LookUpRelatedTicketsModal = ({
  onValueChange,
  initialValues,
  lookUpDialogOpen,
  setLookUpDialogOpen,
}): React.ReactElement => {
  const businessArea = useBusinessArea();

  const [filter, setFilter] = useState({
    search: '',
    status: '',
    fsp: '',
    createdAtRange: '',
    admin: '',
  });
  const debouncedFilter = useDebounce(filter, 500);
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useGrievancesChoiceDataQuery();
  if (!choicesData) return null;
  if (choicesLoading) {
    return <LoadingComponent />;
  }
  return (
    <Formik
      initialValues={initialValues}
      onSubmit={(values) => {
        onValueChange('selectedRelatedTickets', values.selectedRelatedTickets);
        setLookUpDialogOpen(false);
      }}
    >
      {({ submitForm, setFieldValue }) => (
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
              Look up Related Tickets
            </DialogTitle>
          </DialogTitleWrapper>
          <DialogContent>
            <LookUpRelatedTicketsFilters
              choicesData={choicesData}
              filter={debouncedFilter}
              onFilterChange={setFilter}
            />
            <LookUpRelatedTicketsTable
              filter={debouncedFilter}
              businessArea={businessArea}
              setFieldValue={setFieldValue}
              initialValues={initialValues}
            />
          </DialogContent>
          <DialogFooter>
            <DialogActions>
              <Button onClick={() => setLookUpDialogOpen(false)}>CANCEL</Button>
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
      )}
    </Formik>
  );
};
