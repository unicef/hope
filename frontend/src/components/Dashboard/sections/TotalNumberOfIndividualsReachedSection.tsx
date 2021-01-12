import {
  Grid,
  DialogContent,
  DialogTitle,
  Button,
  Box,
} from '@material-ui/core';
import styled from 'styled-components';
import React, { useState } from 'react';
import PersonIcon from '@material-ui/icons/Person';
import { Dialog } from '../../../containers/dialogs/Dialog';
import { DialogActions } from '../../../containers/dialogs/DialogActions';
import {
  CardAmountLink,
  CardTitle,
  DashboardCard,
  IconContainer,
} from '../DashboardCard';
import { DashboardPaper } from '../DashboardPaper';
import { IndividualsWithDisabilityReachedByAgeGroupsChart } from '../charts/IndividualsWithDisabilityReachedByAgeGroupsChart';
import { IndividualsReachedByAgeAndGenderGroupsChart } from '../charts/IndividualsReachedByAgeAndGenderGroupsChart';

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;

const DialogContainer = styled.div`
  width: 700px;
`;
const Title = styled(Box)`
  font-size: 18px;
  font-weight: normal;
`;

export const TotalNumberOfIndividualsReachedSection = (): React.ReactElement => {
  const [dialogOpen, setDialogOpen] = useState(false);

  return (
    <>
      <DashboardCard color='#345DA0'>
        <CardTitle>TOTAL NUMBER OF INDIVIDUALS REACHED</CardTitle>
        <Grid container justify='space-between' alignItems='center'>
          <Grid item>
            <CardAmountLink onClick={() => setDialogOpen(true)}>
              169178378
            </CardAmountLink>
          </Grid>
          <Grid item>
            <IconContainer bg='#D9E2EF' color='#023F90'>
              <PersonIcon fontSize='inherit' />
            </IconContainer>
          </Grid>
        </Grid>
      </DashboardCard>
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
        fullWidth
        maxWidth='md'
      >
        <DialogContent>
          <DialogContainer>
            <Box mb={6}>
              <Title mb={2}>
                Individuals with Disability Reached by Age Groups
              </Title>
              <IndividualsReachedByAgeAndGenderGroupsChart />
            </Box>
            <Box>
              <Title mb={2}>Individuals Reached by Age and Gender Groups</Title>
              <IndividualsWithDisabilityReachedByAgeGroupsChart />
            </Box>
          </DialogContainer>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setDialogOpen(false)}>CLOSE</Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
};
