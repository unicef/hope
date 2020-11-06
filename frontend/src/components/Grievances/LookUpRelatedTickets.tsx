import React, { useState } from 'react';
import SearchIcon from '@material-ui/icons/Search';
import styled from 'styled-components';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@material-ui/core';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { useDebounce } from '../../hooks/useDebounce';
import { useGrievancesChoiceDataQuery } from '../../__generated__/graphql';
import { LookUpRelatedTicketsFilters } from './LookUpRelatedTicketsTable/LookUpRelatedTicketsFilters';
import { LookUpRelatedTicketsTable } from './LookUpRelatedTicketsTable/LookUpRelatedTicketsTable';
import { LoadingComponent } from '../LoadingComponent';
import { LookUpButton } from './LookUpButton';

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;
const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

export const LookUpRelatedTickets = (): React.ReactElement => {
  const [lookUpDialogOpen, setLookUpDialogOpen] = useState(false);
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
    <>
      <LookUpButton
        title='Look up Related Tickets'
        handleClick={() => setLookUpDialogOpen(true)}
      />
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
          />
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setLookUpDialogOpen(false)}>CANCEL</Button>
            <Button
              type='submit'
              color='primary'
              variant='contained'
              onClick={() => null}
              data-cy='button-submit'
            >
              SAVE
            </Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
};
