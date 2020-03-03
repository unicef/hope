import React, {useState} from 'react';
import styled from 'styled-components';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Typography,
} from '@material-ui/core';
import { EditRounded } from '@material-ui/icons';
import { TargetPopulationNode } from '../../../__generated__/graphql';

const ButtonContainer = styled.span`
  margin: 0 ${({ theme }) => theme.spacing(2)}px;
`;

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;

const DialogDescription = styled.div`
  margin: 20px 0;
  font-size: 14px;
  color: rgba(0, 0, 0, 0.54);
`;

export interface InProgressTargetPopulationHeaderButtonsPropTypes {
  targetPopulation: TargetPopulationNode;
  setEditState: Function;
}

export function InProgressTargetPopulationHeaderButtons({
  targetPopulation,
  setEditState,
}: InProgressTargetPopulationHeaderButtonsPropTypes): React.ReactElement {
    const [open, setOpen] = useState(false);
    //TODO: Add finalize query and connect to dialog
    return (
    <div>
      <ButtonContainer>
        <Button
          variant='outlined'
          color='primary'
          startIcon={<EditRounded />}
          onClick={() => setEditState(true)}
        >
          Edit
        </Button>
      </ButtonContainer>
      <ButtonContainer>
        <Button variant='contained' color='primary' onClick={() => setOpen(true)}>
          Finalize
        </Button>
      </ButtonContainer>
      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
      >
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>
            <Typography variant='h6'>Finalize Target Population</Typography>
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogDescription>
            Are you sure you want to push $numberOfHouseholds$ households to CashAssist? This population will be locked (made static).
          </DialogDescription>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setOpen(false)}>CANCEL</Button>
            <Button
              type='submit'
              color='primary'
              variant='contained'
            >
              Finalize
            </Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </div>
  );
}
